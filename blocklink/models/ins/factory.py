from abc import ABCMeta, abstractmethod


# 抽象产品
class Ins(metaclass=ABCMeta):
    @abstractmethod
    def text(self):
        pass


# 抽象工厂
class InsFactory(metaclass=ABCMeta):
    @abstractmethod
    def create(self, **kwargs):
        pass

    @abstractmethod
    def fro_text(self, text):
        pass
