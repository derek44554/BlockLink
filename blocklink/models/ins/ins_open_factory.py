import base64
import json

from blocklink.models.ins.factory import InsFactory
from blocklink.models.ins.ins_open import InsOpen
from blocklink.utils.node_meta import NODE_MEAT
from blocklink.utils.tools import generate_bid, extract_by_space


class InsOpenFactory(InsFactory):
    def create(self, receiver, routing, data, status_code=None, res=None):
        bid = generate_bid()
        sender = NODE_MEAT["bid"]
        return InsOpen(bid=bid, sender=sender, receiver=receiver, routing=routing, data=data, status_code=status_code,
                       res=res)

    def fro_text(self, text):
        """
        Text转模型
        :return:
        """
        bid = extract_by_space(text=text, position=1)
        sender = extract_by_space(text=text, position=2)
        receiver = extract_by_space(text=text, position=3)
        if receiver != NODE_MEAT["bid"] and receiver != NODE_MEAT["bid"][:10] and receiver != "":
            print("Open ins Text转模型 失败")
            return None
        routing = extract_by_space(text=text, position=5)
        data = extract_by_space(text=text, position=6)
        if data is not None:
            data = base64.b64decode(data)
            data = json.loads(data)
        else:
            data = None

        # ---------------------------- 状态吗
        status_code = extract_by_space(text=text, position=7)
        if status_code is not None and status_code != "":
            status_code = int(status_code)

        res = extract_by_space(text=text, position=8)

        return InsOpen(bid=bid, sender=sender, receiver=receiver, routing=routing, data=data, status_code=status_code,
                       res=res)
