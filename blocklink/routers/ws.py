from fastapi import APIRouter
from starlette.websockets import WebSocket, WebSocketDisconnect

from blocklink.models.node.node_manager import NODE_MANAGER
from blocklink.utils.ins_except import InsException
from blocklink.utils.node_message import node_message

ws_app = APIRouter()


@ws_app.websocket("")
async def websocket_endpoint(websocket: WebSocket):
    try:
        await websocket.accept()
        await node_message(websocket=websocket)
    except InsException as e:
        # 已经与对方节点连接 不在进行新的连接
        if e.status_code == 53:
            ...
    except WebSocketDisconnect:
        """断开连接"""
        NODE_MANAGER.disconnect(websocket)