from blocklink.utils.ins_except import InsCertException
from blocklink.models.ins.ins_cert import InsCert
from blocklink.models.node.node import NodeModel
from blocklink.models.signature.signature import SignatureModel
import asyncio
import requests
from blocklink.models.connect.connect_manager import ConnectManager
from blocklink.models.connect.connect import ConnectModel
from blocklink.models.node.node_manager import NodeManager
from blocklink.models.routers.route_block import RouteBlock
from blocklink.utils.node_meta import NodeMeta

connect_route = RouteBlock(route="/connect")


@connect_route.cert("/status")
async def get_connect_status(node_model: NodeModel, ins_cert: InsCert):
    """
    获取所有连接节点的状态信息
    返回格式：
    {
        "total": 总连接数,
        "connected": 直接连接数,
        "registered": 仅注册数,
        "nodes": [
            {
                "bid": "节点BID",
                "status": "connected/registered",
                "has_websocket": true/false,
                "public_address": "公网地址",
                "private_address": "内网地址",
                "mac": "MAC地址"
            }
        ]
    }
    """
    node_manager = NodeManager()
    connect_manager = ConnectManager()

    nodes_status = []
    connected_count = 0
    registered_count = 0

    # 遍历所有已激活的节点
    for bid, node_model in node_manager.active_node.items():
        # 跳过本节点
        if bid == NodeMeta()["bid"]:
            continue

        # 获取连接配置信息
        connect_model = connect_manager[bid]

        # 判断连接状态
        has_websocket = node_model.websocket is not None
        status = "connected" if has_websocket else "registered"

        if has_websocket:
            connected_count += 1
        else:
            registered_count += 1

        node_info = {
            "bid": bid,
            "bid_short": bid[:10],
            "status": status,
            "has_websocket": has_websocket,
            "public_address": connect_model.public_address if connect_model else None,
            "private_address": connect_model.private_address if connect_model else None,
            "mac": connect_model.mac if connect_model else None,
        }

        nodes_status.append(node_info)

    return {
        "total": len(nodes_status),
        "connected": connected_count,
        "registered": registered_count,
        "nodes": nodes_status
    }


@connect_route.cert("/add")
async def add_connect_by_ip(node_model: NodeModel, ins_cert: InsCert):
    """
    通过 IP 地址连接节点
    """
    try:
        address = ins_cert.data.get("address")
        if ":" not in address:
            address += ":24001"

        # 获取节点签名信息
        response = await asyncio.to_thread(
            requests.get,
            f"http://{address}/node/signature",
            timeout=2,
        )
        response_json = response.json()
        signature_model = SignatureModel(data=response_json, **response_json)

        # 签名验证失败或是自己的节点
        if (not signature_model.is_verify) or signature_model.owner == NodeMeta()["bid"]:
            raise InsCertException(node=node_model, ins_cert=ins_cert, status_code=32, content="连接失败")

        # 是否已经是连接状态
        if not ConnectManager()[signature_model.owner]:
            raise InsCertException(node=node_model, ins_cert=ins_cert, status_code=32, content="连接失败")

        data = {
            "bid": signature_model.owner,
            "public_address": address,
        }

        connect_model = ConnectModel(data=data)
        connect_model.save()
        # 建立连接
        await ConnectManager().add_connect(connect_model=connect_model)

        return {}
    except:
        raise InsCertException(node=node_model, ins_cert=ins_cert, status_code=33, content="连接失败")
