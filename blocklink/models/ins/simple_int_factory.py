from blocklink.models.ins.ins_cert_factory import InsCertFactory
from blocklink.models.ins.ins_open_factory import InsOpenFactory
from blocklink.utils.tools import extract_by_space

"""
简单工厂
根据不同的协议调用不同的工厂
"""

class SimpleIntFactory:
    def create(self, text):
        # 协议
        protocol = extract_by_space(text=text, position=4)
        if protocol == "open":
            ins_open_factory = InsOpenFactory()
            ins_open = ins_open_factory.fro_text(text=text)
            return ins_open
        elif protocol == "cert":
            ins_cert_factory = InsCertFactory()
            ins_cert = ins_cert_factory.fro_text(text=text)
            return ins_cert
        else:
            raise
