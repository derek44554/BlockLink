from blocklink.models.routers.route_block_app import RouteApp
from blocklink.strategy.strategy import Strategy
from blocklink.strategy.strategy_manager import StrategyManager

from blocklink.models.routers.route_block_manage import RouteBlockManage, ROUTE_BLOCK_MANAGE
from fastapi import FastAPI

from blocklink.utils.singleton_meta import SingletonMeta
from blocklink.routers.node_api import node_api
from blocklink.routers.bridge import bridge_api
from blocklink.routers.connect import connect_api
from blocklink.routers.ws import ws_app
from blocklink.routers.node import node_route
from blocklink.routers.res import res_route


class BlackAPI(metaclass=SingletonMeta):
    """
    BlackAPI 单例类，负责初始化和管理 FastAPI 应用及其路由、策略等。
    """

    def __init__(self, fast_api: FastAPI):
        """
        初始化 BlackAPI 实例，创建路由管理器和策略管理器。
        """
        self.fast_api: FastAPI  = fast_api
        self.route_block_manage = RouteBlockManage()
        self.strategy_manager = StrategyManager()
        self.open_apis: list[str] = []
        self.apps: list[RouteApp] = []

    def init(self):
        """
        初始化 FastAPI 应用，并注册基础 Block 路由。
        """
        # 注册基础 Block 路由
        self.route_block_manage.add(node_route)
        self.route_block_manage.add(res_route)


        self.fast_api.router.lifespan_context = self.strategy_manager.lifespan
        self.fast_api.lifespan_context = self.strategy_manager.lifespan

        self.load_api()
        self.load_app()

    def add_strategy(self, strategy: Strategy):
        """
        添加策略到策略管理器。
        :param strategy: 需要添加的策略对象
        """
        self.strategy_manager.add(strategy)

    def add_app(self, app: RouteApp):
        """
        添加自定义应用到路由管理器，并注册其所有 API 路由。
        """
        self.route_block_manage.app(app)
        self.apps.append(app)

    def load_app(self):
        for app in self.apps:
            for k, v in app.api_routers.items():
                self.fast_api.include_router(v, prefix=f'{app.name}{k}', tags=[app.title])

    def open_api(self, name: str):
        self.open_apis.append(name)

    def load_api(self):
        """
        根据名称开放指定的 API 路由。
        """
        for name in self.open_apis:
            if name == "ws":
                self.fast_api.include_router(ws_app, prefix='/ws', tags=['Base'])
            if name == "node":
                self.fast_api.include_router(node_api, prefix="/node", tags=['Base'])
            if name == "bridge":
                self.fast_api.include_router(bridge_api, prefix="/bridge", tags=['Base'])
            if name == "connect":
                self.fast_api.include_router(connect_api, prefix="/connect", tags=['Base'])
