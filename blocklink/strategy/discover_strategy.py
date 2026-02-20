import asyncio

from websockets import ClientConnection

from blocklink.models.connect.connect import ConnectModel
from blocklink.models.connect.connect_manager import CONNECT_MANAGER
from blocklink.models.node.node_manager import NODE_MANAGER
from blocklink.models.signature.signature import SignatureModel
from blocklink.strategy.strategy import Strategy

import requests

from blocklink.utils.discover import get_192_subnet_hosts, check_port_open, get_gateway_mac
from blocklink.utils.node_meta import NODE_MEAT

"""
發現策略
-------------
在內網中定時掃描並嘗試與其他節點建立連線。

同步阻塞操作（網段掃描、socket 連線測試、requests HTTP 請求）全部透過
`asyncio.to_thread` 移到執行緒，避免阻塞事件迴圈。
"""


class DiscoverStrategy(Strategy):
    def __init__(self):
        ...

    async def run(self):
        """發現策略主循環（非阻塞版）"""
        port = 24001
        mac = get_gateway_mac()  # 當前網關 MAC
        is_mac_change = False  # 網關 MAC 是否變化

        while True:
            # 1. 掃描 192.168.X.X 網段內所有主機
            hosts = await asyncio.to_thread(get_192_subnet_hosts)

            for host in hosts:
                # 2. 檢查指定埠口是否開放
                is_open = await asyncio.to_thread(check_port_open, host, port)
                if not is_open:
                    continue

                # print(f"[+] {host}:{port} 開放")

                # 3. 取得對方節點簽名
                try:
                    response = await asyncio.to_thread(
                        requests.get,
                        f"http://{host}:{port}/node/signature",
                        timeout=2,
                    )
                    response_json = response.json()
                except Exception:
                    # 請求失敗，忽略
                    continue

                # 4. 建立 / 更新連線模型
                signature_model = SignatureModel(data=response_json, **response_json)

                # 簽名驗證失敗或是自己，直接跳過
                if (not signature_model.is_verify) or signature_model.owner == NODE_MEAT["bid"]:
                    continue

                # 取得既有連線（如果有）
                connect_model = CONNECT_MANAGER[signature_model.owner]

                if connect_model is None:
                    # 尚未建立連線 → 創建並保存
                    data = {
                        "bid": signature_model.owner,
                        "private_address": f"{host}:{port}",
                        "mac": mac,
                    }
                    connect_model = ConnectModel(data=data)
                    connect_model.save()
                    # 新增到管理器並嘗試連線
                    await CONNECT_MANAGER.add_connect(connect_model=connect_model)
                else:
                    # 連線已存在 → 判斷資訊是否需要更新
                    if connect_model.private_address != f"{host}:{port}" or connect_model.mac != mac:
                        connect_model.data["private_address"] = f"{host}:{port}"
                        connect_model.data["mac"] = mac
                        connect_model.private_address = f"{host}:{port}"
                        connect_model.mac = mac
                        connect_model.save()

                # 5. 如 MAC 變化且現有連線為我們主動連線，則強制斷線等待重連
                if is_mac_change:
                    node_model = NODE_MANAGER.get_node(connect_model.bid)
                    if node_model and isinstance(node_model.websocket, ClientConnection):
                        await node_model.websocket.close()

            # ------------------- 週期等待 -------------------
            is_mac_change = False
            for _ in range(60):  # 最長等待 60 * 60 = 3600 秒（1 小時）
                await asyncio.sleep(60)
                # 檢查 MAC 是否改變
                new_mac = get_gateway_mac()
                if new_mac != mac:
                    mac = new_mac
                    is_mac_change = True
                    break
