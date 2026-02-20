from collections import OrderedDict

from blocklink.models.ins.ins_cert import InsCert
from blocklink.models.ins.ins_open import InsOpen
from blocklink.utils.singleton_meta import SingletonMeta

"""
Ins 记录请求的BID
通过BID来判断请求是否需要跳过不进行处理 还是继续处理
"""


class InsRecord(metaclass=SingletonMeta):
    def __init__(self):
        # {"bid": 1}
        # 储存指令的BID记录
        self.bids = OrderedDict()

    def add_ins(self, ins: InsOpen | InsCert):
        """
        添加指令的BID记录
        """

        if ins.bid in self.bids:
            return

        self.bids[ins.bid] = True

        if len(self.bids) >= 10000:
            self.bids.popitem(last=False)  # 删除最早的

    def is_skip(self, ins: InsOpen | InsCert):
        """
        是否 进行跳过 不处理
        """

        # 如果BID不在记录中 则不进行跳过 继续处理
        if ins.bid not in self.bids:
            return False

        return True


INS_RECORD = InsRecord()
