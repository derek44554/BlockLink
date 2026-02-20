from blocklink.models.node.node_manager import NODE_MANAGER
from blocklink.utils.ins_except import InsException
from blocklink.utils.node_meta import NODE_MEAT
from blocklink.utils.tools import extract_by_space

"""
决定用哪个节点来发送指令
"""

async def node_send_v2(receiver, data):
    # 用于发布的节点
    node = NODE_MANAGER.get_node(receiver)

    # 是否与指令接收节点直接相连
    if node and node.websocket:
        await node.send_text(data)
        return node

    # ----------------- 通过桥节点进行转发
    # 获取消息的发送者 bid (position 2)
    sender_bid = extract_by_space(text=data, position=2)
    local_bid = NODE_MEAT["bid"]
    
    # 使用列表推导式一次性过滤出可用的桥节点
    bridge_nodes = [
        node for bid, node in NODE_MANAGER.active_node.items()
        if bid != local_bid  # 跳过本节点
        and bid != sender_bid  # 跳过原始发送者节点
        and node.websocket  # 存在 websocket 连接
        and node.info.get("pivot") is True  # 是桥节点
    ]

    if not bridge_nodes:
        raise InsException(ins=None, status_code=62, content=f"接收者 {receiver} 没有可以转发的节点")

    # 向所有桥节点发送指令
    for node_model in bridge_nodes:
        await node_model.send_text(data)

    return None