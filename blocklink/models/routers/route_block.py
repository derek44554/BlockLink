from typing import Callable, Dict

from starlette.websockets import WebSocket

from blocklink.models.ins.ins_cert_factory import InsCertFactory, INS_CERT_FACTORY
from blocklink.models.ins.ins_open import InsOpen
from blocklink.models.ins.ins_open_factory import InsOpenFactory
from blocklink.utils.send import execute_send_ins
from websockets import ClientConnection
from blocklink.utils.node_meta import NODE_MEAT

"""
Block路由
匹配协议与路由
注册函数
"""


class RouteBlock:
    def __init__(self, route):
        self.route = route
        self.route_open: Dict[str, Callable] = {}  # OPEN 协议路由
        self.route_cert: Dict[str, Callable] = {}  # CERT 协议路由

    def open(self, routing_key: str):
        """装饰器 用于注册路由处理函数"""

        def decorator(func: Callable):
            async def wrapper(websocket: WebSocket | ClientConnection, ins_open: InsOpen, *args, **kwargs):
                result = await func(websocket, ins_open, *args, **kwargs)
                if isinstance(result, dict):
                    ins_open_factory = InsOpenFactory()
                    ins_open_send = ins_open_factory.create(
                        receiver=ins_open.sender,
                        routing="/res/data",
                        data=result,
                        status_code=21,
                        res=ins_open.bid
                    )
                    if type(websocket) == WebSocket:
                        await websocket.send_text(ins_open_send.text)
                    elif type(websocket) == ClientConnection:
                        await websocket.send(ins_open_send.text)
                    else:
                        # 若响应目标是本地节点，直接注入 RES_FUTURES
                        if ins_open_send.receiver == NODE_MEAT["bid"]:
                            from blocklink.utils.res_futures import RES_FUTURES
                            RES_FUTURES.res_ins(ins_open_send)
                        else:
                            await execute_send_ins(ins=ins_open_send, is_res=False)

            self.route_open[routing_key] = wrapper
            return wrapper

        return decorator

    def cert(self, routing_key: str):
        """装饰器 用于注册路由处理函数"""

        def decorator(func: Callable):
            # ----------------------- 返回函数后处理的内容
            # 主要用于返回响应的指令
            async def wrapper(node_model, ins_cert, *args, **kwargs):
                result = await func(node_model, ins_cert, *args, **kwargs)

                # ✅ 统一包装响应
                if isinstance(result, dict):
                    ins_cert_res = INS_CERT_FACTORY.create(
                        receiver=ins_cert.sender,
                        routing="/res/data",
                        data=result,
                        status_code=21,
                        res=ins_cert.bid
                    )
                    # 若响应目标是本地节点，直接注入 RES_FUTURES
                    if ins_cert_res.receiver == NODE_MEAT["bid"]:
                        from blocklink.utils.res_futures import RES_FUTURES
                        RES_FUTURES.res_ins(ins_cert_res)
                    else:
                        await execute_send_ins(ins=ins_cert_res, is_res=False)

            self.route_cert[routing_key] = wrapper
            return wrapper

        return decorator
