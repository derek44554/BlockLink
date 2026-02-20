from typing import List, Dict
import os

from blocklink.models.node.node import NodeModel
from blocklink.models.signature.signature import SignatureModel
from blocklink.utils.node_meta import NODE_MEAT
from blocklink.utils.singleton_meta import SingletonMeta

"""
节点管理
"""


class NodeManager(metaclass=SingletonMeta):
    def __init__(self):
        # 已注册节点
        self.active_node: Dict[str, NodeModel] = {}
        # 未注册节点
        self.not_active_node: Dict[str, NodeModel] = {}

        self.start()

    def start(self):
        """将本节点加入其中"""
        signature_model = SignatureModel(NODE_MEAT.signature, **NODE_MEAT.signature)
        node_model = NodeModel(bid=NODE_MEAT["bid"], websocket=None, signature_model=signature_model, encryption_key=os.urandom(32))
        self.active_node[NODE_MEAT["bid"]] = node_model

    def active(self, node_model: NodeModel):
        """
        增加 NodeModel
        :param node_model:
        :return:
        """
        # 是否 在未注册中存在
        if self.not_active_node.get(node_model.bid):
            del self.not_active_node[node_model.bid]
        self.active_node[node_model.bid] = node_model

    def not_active(self, node_model: NodeModel):
        """
        添加未激活节点
        :param node_model:
        :return:
        """
        self.not_active_node[node_model.bid] = node_model

    def disconnect(self, websocket):
        """
        断开 移除NodeModel中的websocket
        :param websocket:
        :return:
        """
        # 遍历全部 激活节点
        for k, v in self.active_node.items():
            # 判断 websocket 是否在哪个节点中
            if v.websocket == websocket:
                print(f"断开连接 {k}")
                # 移除 websocket
                v.websocket = None

        # 遍历全部 未激活节点
        for k, v in self.not_active_node.items():
            # 判断 websocket 是否在哪个节点中
            if v.websocket == websocket:
                print(f"断开连接 {k}")
                # 移除 websocket
                v.websocket = None

    def is_active(self, bid, is_connect=None):
        """
        BID是否已注册激活
        :param bid: BID
        :param is_connect: 是否websocket不为空
        :return:
        """
        node_model = self.active_node.get(bid)
        if node_model is None:
            return False
        # 要求websocket不为空
        if is_connect:
            if node_model.websocket is None:
                return False

        return True

    def get_node(self, bid):
        """
        通过节点BID获取节点
        """
        # 前10为字符bid查找节点
        if len(bid) == 10:
            for k, v in self.active_node.items():
                if k[:10] == bid:
                    return v
        else:
            # 已正常的节点完全匹配bid
            return NODE_MANAGER.active_node.get(bid)

        return None


NODE_MANAGER = NodeManager()
