import asyncio
import base64
from websockets.legacy.exceptions import InvalidStatusCode
from blocklink.adapters.ins.node import send_ins_node_info
from blocklink.models.node.node import NodeModel
from blocklink.models.node.node_manager import NODE_MANAGER, NodeManager
from blocklink.models.signature.signature_manager import SIGNATURE_MANAGER
from blocklink.utils.connection import connection_node
from blocklink.utils.discover import get_gateway_mac
from blocklink.utils.ins_except import InsException
from blocklink.utils.node_message import node_message
from blocklink.utils.register_node import register_node
from blocklink.utils.tools import yaml_data, save_to_yaml
import websockets
import socket

"""
连接信息的节点信息
用于处理与其他节点连接
"""


class ConnectModel:
    def __init__(self, data):
        self.data = data
        self.bid = data["bid"]

        self.public_address = data.get("public_address")
        self.private_address = data.get("private_address")
        self.mac = data.get("mac")
        self.key_hex = data.get("key_hex")

        self.sleep = 30  # 休眠时间


    def uni_register(self):
        """
        单向注册
        加载本地已保存节点进行本节点单向注册
        :return:
        """
        # 是否 加密存在
        if self.key_hex:
            # 获取本地存储的对方节点的证书
            signature_model = SIGNATURE_MANAGER.get_signature_by_owner(self.bid)

            # 证书存在
            if signature_model:
                encryption_key = bytes.fromhex(self.key_hex)
                node_model = NodeModel(self.bid, websocket=None, signature_model=signature_model,
                                       encryption_key=encryption_key)
                NODE_MANAGER.active(node_model=node_model)
                print(f"单向注册 {self.bid}")

    def save(self):
        """保存信息"""
        save_to_yaml(self.data, f"data/connect/{self.bid}.yml")

    async def connect(self):
        """
        连接
        不断尝试连接
        如果已注册但没有直接连接 会不断尝试是否可以直接连接 只需要其他地方给予最新的 private_address地址 或 public_address地址
        :return:
        """
        while True:
            # ------------------------- 否 已连接
            if not NODE_MANAGER.is_active(self.bid, is_connect=True):
                # 有 内网IP
                if self.private_address is not None and self.mac == get_gateway_mac():
                    await self.connect_address(self.private_address)

                # 有 公网IP
                if self.public_address:
                    await self.connect_address(self.public_address)

            # ------------------------- 否 此BID已经注册
            if not NODE_MANAGER.is_active(self.bid):
                # 进行注册
                await self.connect_register()

            # ------------------------- 休眠
            # 是否 休眠时间小于600秒
            if self.sleep < 600:
                # 增加休眠时间
                self.sleep *= 1.3
            await asyncio.sleep(self.sleep)

    async def connect_address(self, address):
        """与对方直接连接"""
        websocket = None

        try:
            websocket = await websockets.connect(f"ws://{address}/ws", max_size=10 * 1024 * 1024)

            # 进行注册
            node_model = await connection_node(websocket)
            # ---------------------- step 1: 启动 node_message 协程，但不等它
            task = asyncio.create_task(node_message(websocket=node_model.websocket))

            # ---------------------- 保存
            self.key_hex = node_model.encryption_key.hex()
            self.data["key_hex"] = self.key_hex
            self.save()

            # ----------------------
            # 连接成功后休眠时间重置为30秒
            self.sleep = 30
            print(f"连接成功 {node_model.bid} {address}")

            # ---------------------- step 2: 这里执行你自己的操作
            # 发送节点信息
            await send_ins_node_info(self.bid)
            # ---------------------- step 3: 等 node_message 正常运行完成
            await task
        except (
                websockets.exceptions.InvalidMessage,  # 握手响应格式错误
                InvalidStatusCode,  # 握手时服务端返回非101状态码
                ConnectionRefusedError,  # TCP 连接被拒绝
                TimeoutError,  # 握手超时
                socket.gaierror,  # DNS 错误
        ) as e:
            """无法与对方连接"""
            print(f"连接失败 {address} 稍后重试")

        except websockets.exceptions.WebSocketException as e:
            """连接断开"""
            """"需要这个异常捕获 不能去掉"""
            ...
        except Exception as e:
            print(f"需要处理的错误 {e}")

        # ---------------------- 断开处理
        """运行到这个地方就代表断开了"""
        if websocket is not None:
            # 断开连接
            await websocket.close()
            # 断开节点内的 websocket
            NODE_MANAGER.disconnect(websocket)

    async def connect_register(self):
        """与对方节点注册"""
        try:
            # 开始注册
            node_model = await register_node(self.bid)

            # ---------------------- 保存
            self.key_hex = node_model.encryption_key.hex()
            self.data["key_hex"] = self.key_hex
            self.save()

            print(f"注册成功 {self.bid}")
        except InsException as e:
            print(f"注册失败 {self.bid}, 稍后后重试")
