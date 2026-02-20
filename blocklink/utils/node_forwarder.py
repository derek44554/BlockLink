from starlette.websockets import WebSocket
from websockets import ClientConnection

from blocklink.models.ins.ins_cert_factory import INS_CERT_FACTORY
from blocklink.models.node.node_manager import NODE_MANAGER
from blocklink.utils.ins_except import InsOpenException, InsCertException
from blocklink.utils.node_meta import NODE_MEAT

"""
转发指令
"""

async def forward_to_node(websocket, data, sender, receiver, int_bid):
    """将消息转发给目标节点，若节点未注册则抛出异常"""
    if NODE_MEAT.node.get("bridge") != True:
        ins_cert_send = INS_CERT_FACTORY.create(
            receiver=sender,
            routing="/res/data",
            data={"v": "节点不负责转发此指令"},
            status_code=63,
            res=int_bid,
        )
        raise InsCertException(node=NODE_MANAGER.active_node[receiver], ins_cert=ins_cert_send, status_code=61)

    sender_node_model = NODE_MANAGER.get_node(sender)
    # 如果发送者节点未注册，抛出 InsOpenException 异常
    if sender_node_model is None:
        ins_cert_send = INS_CERT_FACTORY.create(
            receiver=sender,
            routing="/res/data",
            data={"v": "节点需要先注册才能被转发指令"},
            status_code=51,
            res=int_bid,
        )
        raise InsOpenException(websocket=websocket, ins_open=ins_cert_send, status_code=51)

    # 获取目标节点，如果未注册则抛出 InsCertException 异常
    node_model = NODE_MANAGER.get_node(receiver)
    if node_model is None:
        ins_cert_send = INS_CERT_FACTORY.create(
            receiver=sender,
            routing="/res/data",
            data={"v": "节点需要先注册才能被转发指令"},
            status_code=51,
            res=int_bid,
        )
        raise InsCertException(node=NODE_MANAGER.active_node[receiver], ins_cert=ins_cert_send, status_code=61)

    if type(websocket) == WebSocket:
        await node_model.send_text(data)
    elif type(websocket) == ClientConnection:
        await node_model.send(data)

