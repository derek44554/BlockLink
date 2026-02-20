from abc import abstractmethod, ABCMeta

"""
策略
"""

class Strategy(metaclass=ABCMeta):
    @abstractmethod
    async def run(self):
        pass
