from blocklink.models.ins.simple_int_factory import SimpleIntFactory
from blocklink.models.routers.route_block_manage import ROUTE_BLOCK_MANAGE
from blocklink.utils.node_meta import NodeMeta
from fastapi import WebSocket, WebSocketDisconnect
from blocklink.utils.node_forwarder import forward_to_node
from blocklink.utils.node_send import node_send_v2
from blocklink.utils.send import execute_send_ins
from blocklink.utils.tools import extract_by_space
from websockets import ClientConnection
import asyncio

"""
等待websocket发送消息
"""

send_lock = asyncio.Lock()          # 避免并发 send 乱序

async def process_msg(websocket, data):
    # 这里可以放心做 CPU/IO 操作；若要回写同一个 websocket，记得加锁
    int_bid   = extract_by_space(text=data, position=1)
    receiver  = extract_by_space(text=data, position=3)

    # 是否 不在本节点处理
    if receiver != NodeMeta()["bid"] and receiver != NodeMeta()["bid"][:10] and receiver != "":
        await node_send_v2(receiver=receiver, data=data)
        return

    simple_int_factory = SimpleIntFactory()
    ins = simple_int_factory.create(text=data)

    await execute_send_ins(ins=ins, websocket=websocket)

async def node_message(websocket: WebSocket | ClientConnection):
    while True:
        data = (await websocket.receive_text()
                if isinstance(websocket, WebSocket)
                else await websocket.recv())


        # **关键行**：不要 await，直接丢给事件循环
        asyncio.create_task(process_msg(websocket, data))
