from blocklink.utils.cryptography import load_pem_to_public_key, public_key_to_binary
from blocklink.utils.verify import signature_verify

"""
签名模型
"""


class SignatureModel:
    def __init__(self, data, **kwargs):
        self.data = data
        self.bid = kwargs.get('bid')
        self.model = kwargs.get('model')
        self.signature = kwargs.get('signature')  # 签名数据
        self.owner = kwargs.get('owner')  # 拥有者BID
        self.permission_level = int(kwargs["permission_level"])  # 权限等级
        self.validity_period = kwargs.get('validity_period')  # 有效期
        self.public_key_pem = kwargs.get('public_key_pem')  # 公钥 pem格式
        self.public_key = load_pem_to_public_key(self.public_key_pem)  # 公钥对象

    @property
    def is_verify(self) -> bool:
        """
        验证签名
        :return:
        """
        data = b""
        data += self.owner.encode('utf-8')
        data += b" "
        data += self.permission_level.to_bytes(2, byteorder='big')
        data += b" "
        data += self.validity_period.encode('utf-8')
        data += b" "
        data += public_key_to_binary(self.public_key)  # 二进公钥

        is_pass = signature_verify(
            signature_base64 = self.signature,
            data = data
        )

        return is_pass