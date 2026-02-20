import asyncio
from typing import Dict

from blocklink.models.connect.connect import ConnectModel
from blocklink.utils.singleton_meta import SingletonMeta
from blocklink.utils.tools import get_yaml_files

"""
连接管理
"""


class ConnectManager(metaclass=SingletonMeta):
    def __init__(self):
        self.connects: Dict[str, ConnectModel] = {}
        self.init()

    def __getitem__(self, bid):
        return self.connects.get(bid, None)

    def init(self):
        """初始化"""
        connects_data = get_yaml_files("data/connect")
        for obj in connects_data:
            # 连接模型
            connect_model = ConnectModel(data=obj["data"])
            # 单向注册
            connect_model.uni_register()
            self.add(connect_model)

    def add(self, connect_model: ConnectModel):
        """添加 ConnectModel"""
        self.connects[connect_model.bid] = connect_model

    async def connect(self):
        """启动 ConnectModel 连接"""
        tasks = []

        for k, v in self.connects.items():
            tasks.append(v.connect())

        await asyncio.gather(*tasks)

    async def add_connect(self, connect_model: ConnectModel):
        """添加 启动 ConnectModel 连接"""
        self.connects[connect_model.bid] = connect_model
        await connect_model.connect()

