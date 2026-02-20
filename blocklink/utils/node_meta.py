import os
from blocklink.utils.singleton_meta import SingletonMeta
from blocklink.utils.cryptography import load_public_key, load_private_key
from blocklink.utils.tools import yaml_data

"""
本节点的基本信息
单列模式
全局代码可访问配置
"""

class NodeMeta(metaclass=SingletonMeta):
    def __init__(self):
        self.node = yaml_data("config/node.yml")  # 节点信息
        self.top_verify_public_pey = load_public_key(path=os.getenv("TOP_VERIFY_PUBLIC_PEY_PATH"))  # 顶级验证公钥
        self.node_private_pey = load_private_key(path=os.getenv("NODE_PRIVATE_PEY_PATH"))  # 节点私钥
        self.signature = yaml_data(os.getenv("SIGNATURE_PATH"))  # 签名


    def __getitem__(self, name):
        return self.node.get(name, None)


NODE_MEAT = NodeMeta()
