from typing import Dict

from blocklink.models.signature.signature import SignatureModel
from blocklink.utils.singleton_meta import SingletonMeta
from blocklink.utils.tools import get_yaml_files

"""
证书管理
"""


class SignatureManager(metaclass=SingletonMeta):
    def __init__(self):
        self.signatures: Dict[str, SignatureModel] = {}
        self.init()

    def init(self):
        """初始化"""
        signature_data = get_yaml_files("data/signature")
        for obj in signature_data:
            signature_model = SignatureModel(data=obj["data"], **obj["data"])
            self.signatures[signature_model.bid] = signature_model

    def get_signature_by_owner(self, owner):
        """获取证书 通过 owner拥有者"""
        for k, v in self.signatures.items():
            if v.owner == owner:
                return v

        return None


SIGNATURE_MANAGER = SignatureManager()
