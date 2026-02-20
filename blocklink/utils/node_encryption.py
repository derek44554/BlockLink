from blocklink.models.node.node_manager import NodeManager

"""
发送加密
"""


def node_encryption_base64(bid, data: bytes):
    """
    通过节点bid进行加密数据
    :param bid: 对方节点bid 被信任的节点
    :param data: 要被加密的字节
    :return:
    """
    node_manager = NodeManager()
    none_model = node_manager.get_node(bid)
    encrypting_data = none_model.encryption_base64(data)
    return encrypting_data

def node_decryption_base64(bid, data: str):
    node_manager = NodeManager()

    none_model = node_manager.get_node(bid)
    decrypt_data = none_model.decrypt_base64(data)
    return decrypt_data
