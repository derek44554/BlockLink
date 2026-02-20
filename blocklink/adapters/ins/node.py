from blocklink.models.ins.ins_cert_factory import InsCertFactory
from blocklink.utils.node_meta import NODE_MEAT
from blocklink.utils.send import execute_send_ins


async def send_ins_node_info(receiver):
    """
    发送本节点信息给对方节点
    :param receiver: 接收的节点
    :return:
    """
    # -------------------- 获取对方节点信息
    info_ins = InsCertFactory().create(receiver=receiver, routing="/node/res_info", data=NODE_MEAT.node)
    await execute_send_ins(ins=info_ins)
