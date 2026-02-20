import base64
import json

from blocklink.models.ins.factory import Ins
from blocklink.utils.cryptography import datetime_converter
from blocklink.utils.node_encryption import node_encryption_base64


class InsCert(Ins):
    protocol = "cert"

    def __init__(self, bid, sender, receiver, routing, data,status_code, res):
        self.bid = bid  # 指令BID
        self.sender = sender  # 发送者BID
        self.receiver = receiver  # 接收者BID
        self.routing = routing  # 路由
        self.data: dict|None = data  # 数据
        self.status_code = status_code  # 状态码
        self.res = res  # 响应BID

    @property
    def text(self) -> str:
        """
        模型转用于传输的Text
        :return:
        """
        return_data = ""
        return_data += f"{self.bid} "  # BID
        return_data += f"{self.sender} "  # 发送者BID
        return_data += f"{self.receiver} "  # 接收者BID
        return_data += f"{self.protocol} "  # 协议
        # 路由 data_base64 响应bid
        # 准备加密的数据
        prepare_encrypt = ""
        # 路由
        prepare_encrypt += f"{self.routing} "
        # 数据 data_base64
        if self.data is not None:
            data = json.dumps(self.data, indent=4, default=datetime_converter)
            data = str(base64.b64encode(data.encode('utf-8')), 'utf-8')
            prepare_encrypt += f"{data} "
        else:
            prepare_encrypt += " "

        # 状态码
        if self.status_code is not None:
            prepare_encrypt += f"{self.status_code} "
        else:
            prepare_encrypt += f" "  # 一定要两个空格

        # 响应BID
        if self.res is not None:
            prepare_encrypt += f"{self.res} "

        prepare_encrypt_bytes = prepare_encrypt.encode(encoding='utf-8')
        encrypting_data = node_encryption_base64(self.receiver, data=prepare_encrypt_bytes)
        return_data += f"{encrypting_data}"  # 加密后的数据

        return return_data
