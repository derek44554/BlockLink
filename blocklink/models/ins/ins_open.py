import base64
import json

from blocklink.models.ins.factory import Ins
from blocklink.utils.cryptography import datetime_converter


class InsOpen(Ins):
    protocol = "open"
    def __init__(self, bid,sender, receiver, routing, data, status_code=None, res=None):
        self.bid = bid  # 指令BID
        self.sender = sender  # 发送者BID
        self.receiver = receiver  # 接收者BID
        self.routing = routing  # 路由
        self.data: dict =data  # 数据
        self.status_code = status_code  # 状态码
        self.res = res  # 响应BID

    @property
    def text(self) -> str:
        """
        模型转用于传输的Text
        :return:
        """
        return_data = ""
        # 根据不同协议进行不同封装s s
        return_data += f"{self.bid} "  # BID
        return_data += f"{self.sender} "  # 发送者BID
        return_data += f"{self.receiver} "  # 接收者BID
        return_data += f"{self.protocol} "  # 协议
        return_data += f"{self.routing} "  # 路由
        # 数据
        if self.data is not None:
            data = json.dumps(self.data, indent=4, default=datetime_converter)
            data = str(base64.b64encode(data.encode('utf-8')),'utf-8')
            return_data += f"{data} "
        else:
            return_data += " "

        if self.status_code is not None:
            return_data += f"{self.status_code} "
        else:
            return_data += " "  # 一定要两个空格

        # 响应BID
        if self.res is not None:
            return_data += f"{self.res} "


        return return_data
