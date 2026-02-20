from blocklink.models.ins.factory import Ins
from blocklink.models.ins.ins_cert import InsCert
from blocklink.models.ins.ins_cert_factory import InsCertFactory
from blocklink.models.ins.ins_open import InsOpen
from blocklink.models.ins.ins_open_factory import InsOpenFactory
from blocklink.models.node.node import NodeModel

"""
指令异常
"""

# 指令异常 无需协议类型 无需返回给其他节点
class InsException(Exception):
    def __init__(self,  status_code: int, ins: Ins=None, content=None):
        self.ins = ins
        self.status_code = status_code
        self.content = content


# 指令异常 以Open协议返回
class InsOpenException(Exception):
    def __init__(self, websocket, ins_open: InsOpen, status_code: int, content=None):
        self.websocket = websocket
        self.ins_open = ins_open
        self.status_code = status_code
        self.content = content

    async def send(self):
        ins_open_factory = InsOpenFactory()
        ins_open_send = ins_open_factory.create(
            receiver=self.ins_open.sender,
            routing="/res/data",
            status_code=self.status_code,
            data={"v": self.content},
            res=self.ins_open.bid,
        )
        await self.websocket.send_text(ins_open_send.text)


class InsCertException(Exception):
    def __init__(self, node: NodeModel, ins_cert: InsCert, status_code: int, content=None):
        self.node = node
        self.ins_cert = ins_cert
        self.status_code = status_code
        self.content = content
        print(f"错误状态码 {status_code}")

    async def send(self):
        ins_cert_factory = InsCertFactory()
        ins_cert_send = ins_cert_factory.create(
            receiver=self.ins_cert.sender,
            routing="/res/data",
            data={"v": self.content},
            status_code=self.status_code,
            res=self.ins_cert.bid,
        )
        await self.node.send_text(ins_cert_send.text)
