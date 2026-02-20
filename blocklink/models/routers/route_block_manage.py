from blocklink.models.ins.factory import Ins
from blocklink.models.ins.ins_cert import InsCert
from blocklink.models.ins.ins_open import InsOpen
from blocklink.models.ins.simple_int_factory import SimpleIntFactory
from blocklink.models.node.node_manager import NodeManager
from blocklink.models.routers.route_block import RouteBlock
from blocklink.models.routers.route_block_app import RouteApp
from blocklink.utils.ins_except import InsOpenException, InsCertException
from blocklink.utils.singleton_meta import SingletonMeta

"""
Block路由
匹配协议与路由
注册函数
"""


class RouteBlockManage(metaclass=SingletonMeta):
    def __init__(self):
        self.route_blocks: list[RouteBlock] = []
        self.route_block_apps: list[RouteApp] = []

    def add(self, route_block: RouteBlock):
        """
        添加 RouteBlock
        :param route_block:
        :return:
        """
        self.route_blocks.append(route_block)

    def app(self, route_block_app: RouteApp):
        """
        添加 RouteBlock
        :param route_block:
        :return:
        """
        self.route_block_apps.append(route_block_app)

    def match(self, routing, ins: Ins):
        """
        匹配
        匹配对应的函数
        :param routing:
        :param ins:
        :return:
        """
        for route_block in self.route_blocks:
            # 找到对应线路
            if routing.startswith(route_block.route):
                # 从开头去掉指定的子字符串
                routing_next = routing[len(route_block.route):]
                if type(ins) is InsOpen:
                    handler = route_block.route_open.get(routing_next)
                    if handler:
                        return handler
                elif type(ins) is InsCert:
                    handler = route_block.route_cert.get(routing_next)
                    if handler:
                        return handler
                else:
                    raise

        for route_block_app in self.route_block_apps:
            if routing.startswith(route_block_app.name):
                for route_block in route_block_app.route_blocks:
                    if routing.startswith(route_block_app.name+route_block.route):
                        routing_next = routing[len(route_block_app.name+route_block.route):]
                        if type(ins) is InsOpen:
                            handler = route_block.route_open.get(routing_next)
                            if handler:
                                return handler
                        elif type(ins) is InsCert:
                            handler = route_block.route_cert.get(routing_next)
                            if handler:
                                return handler
                        else:
                                raise
        return None

    async def get_handler(self, websocket, ins: InsOpen | InsCert):
        """
        匹配对应的路由函数 会根据指令的 "协议" 与 "路由" 去匹配
        :param websocket:
        :param data:
        :return:
        """
        # simple_int_factory = SimpleIntFactory()
        # ins = simple_int_factory.create(text=data)
        # -------------------------- InsOpen
        if type(ins) == InsOpen:
            print(f"路由 {ins.routing}")
            # handler = self.route_open.get(ins.routing)
            handler = self.match(ins.routing, ins)
            if handler is None:
                raise InsOpenException(websocket=websocket, ins_open=ins, status_code=41)
            await handler(websocket, ins)

        # -------------------------- InsCert
        elif type(ins) == InsCert:
            print(f"路由 {ins.routing}")
            node_manager = NodeManager()
            node = node_manager.get_node(ins.sender)
            if node is None:
                raise InsOpenException(websocket=websocket, ins_open=ins, status_code=51)
            # handler = self.route_cert.get(ins.routing)
            handler = self.match(ins.routing, ins)
            if handler is None:
                raise InsCertException(node=websocket, ins_cert=ins, status_code=41)
            await handler(node, ins)
        else:
            raise

ROUTE_BLOCK_MANAGE = RouteBlockManage()