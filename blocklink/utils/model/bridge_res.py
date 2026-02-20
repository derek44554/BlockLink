"""
桥响应模型
"""


class BridgeRes:
    def __init__(self, bid, status_code, data, sender, res):
        self.bid = bid
        self.status_code = status_code
        self.data = data
        self.sender = sender
        self.res = res

    @property
    def dict(self) -> dict:
        return {
            "bid": self.bid,
            "status_code": self.status_code,
            "data": self.data,
            "sender": self.sender,
            "res": self.res,
        }
