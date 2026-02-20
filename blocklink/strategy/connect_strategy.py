from blocklink.models.connect.connect_manager import ConnectManager
from blocklink.strategy.strategy import Strategy

"""
连接策略

用于主动连接其他节点的策略
"""


class ConnectStrategy(Strategy):
    def __init__(self):
        ...

    async def run(self):
        # 节点连接
        await ConnectManager().connect()
