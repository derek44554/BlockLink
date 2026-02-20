import base64
import json

from blocklink.models.ins.factory import InsFactory
from blocklink.models.ins.ins_cert import InsCert
from blocklink.utils.node_encryption import node_decryption_base64
from blocklink.utils.node_meta import NODE_MEAT
from blocklink.utils.tools import generate_bid, extract_by_space


class InsCertFactory(InsFactory):
    def create(self, receiver, routing, data, status_code=None,res=None):
        bid = generate_bid()
        sender = NODE_MEAT["bid"]
        return InsCert(bid=bid, sender=sender, receiver=receiver, routing=routing, data=data, res=res, status_code=status_code)

    def fro_text(self, text):
        """
        Text转模型
        :return:
        """
        bid = extract_by_space(text=text, position=1)
        sender = extract_by_space(text=text, position=2)
        receiver = extract_by_space(text=text, position=3)
        if receiver != NODE_MEAT["bid"] and receiver != NODE_MEAT["bid"][:10] and receiver != "":
            print("Cert ins Text转模型 失败")
            return None

        # 加密数据
        encrypting_data = extract_by_space(text=text, position=5)
        # 进行解密
        decrypt_data = node_decryption_base64(bid=sender, data=encrypting_data)
        # 转为字符串
        decrypt_str = str(decrypt_data, encoding='utf-8')

        # 路由
        routing = extract_by_space(text=decrypt_str, position=1)
        data = extract_by_space(text=decrypt_str, position=2)
        if data is not None:
            data = base64.b64decode(data)
            data = json.loads(data)
        else:
            data = None

        status_code = extract_by_space(text=decrypt_str, position=3)
        if status_code is not None and status_code != "":
            status_code = int(status_code)

        res = extract_by_space(text=decrypt_str, position=4)

        return InsCert(bid=bid, sender=sender, receiver=receiver, routing=routing, data=data,status_code=status_code, res=res)

INS_CERT_FACTORY = InsCertFactory()