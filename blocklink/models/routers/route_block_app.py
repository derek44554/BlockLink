from fastapi import APIRouter
from blocklink.models.routers.route_block import RouteBlock


class RouteApp:
    def __init__(self, name: str, title:str):
        self.name: str = name
        self.title = title
        self.route_blocks: list[RouteBlock] = []
        # {"name": obj}
        self.api_routers: dict = {}

    def add(self, route_block):
        self.route_blocks.append(route_block)

    def add_api(self, name: str, api_router: APIRouter):
        self.api_routers[name] = api_router

