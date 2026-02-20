import os
from blocklink.models.ins.ins_open_factory import InsOpenFactory
from blocklink.models.node.node import NodeModel
from blocklink.models.node.node_manager import NodeManager
from blocklink.models.signature.signature import SignatureModel
from blocklink.utils.node_meta import NodeMeta
from blocklink.utils.send import execute_send_ins
from blocklink.utils.cryptography import encrypt_with_public_key_base64, decrypt_with_private_key_base64, \
    encrypt_with_symmetric_key_base64
from blocklink.utils.tools import save_to_yaml

"""
连接一个跨越的远程节点
"""


async def register_node(node_bid):
    # --------------- 获取对方证书
    ins_open_factory = InsOpenFactory()
    get_signature_ins_model = ins_open_factory.create(
        receiver=node_bid,
        routing="/node/signature",
        data={},
    )
    # 指令发送
    # 接收 包含模型的证书的指令模型
    signature_ins_model = await execute_send_ins(ins=get_signature_ins_model,is_res=True)
    # 创建签名对象
    signature_model = SignatureModel(data=signature_ins_model.data,**signature_ins_model.data)

    # 证书不正确 抛出异常
    if signature_model.is_verify is not True:
        raise

    # --------------- 随机挑战 准备验证对方身份
    # 生成的随机挑战
    challenge_original = os.urandom(32)

    # 使用对方公钥加密
    challenge_ciphertext_base64 = encrypt_with_public_key_base64(public_key=signature_model.public_key,
                                                                 data_bytes=challenge_original + NodeMeta()["bid"].encode(
                                                                     encoding='utf-8'))

    challenge_data = {
        "challenge": challenge_ciphertext_base64,  # 随机挑战
        "signature": NodeMeta().signature,  # 签名

    }

    # 随机挑战发送的指令模型
    challenge_send_ins_model = ins_open_factory.create(receiver=signature_model.owner,
                                               routing="/node/register/start", data=challenge_data)


    # --------------- 验证对方身份
    # 接收随机挑战来验证对方身份 与 加密Key
    # 接收的内容被本节点公钥加密
    # 发送指令
    challenge_and_key_ins_model = await execute_send_ins(ins=challenge_send_ins_model, is_res=True)

    challenge_and_key = decrypt_with_private_key_base64(private_key=NodeMeta().node_private_pey,
                                                        encrypted_base64=challenge_and_key_ins_model.data["v"])
    challenge = challenge_and_key[:32]  # 随机挑战
    encryption_key = challenge_and_key[32:]  # 对称加密Key

    # 是否 随机挑战验证失败
    if challenge_original != challenge:
        raise

    # --------------- 使用对称加密来让对方节点信任本节点
    ok_base64 = encrypt_with_symmetric_key_base64(key=encryption_key, data=b'ok')
    ok_send_ins_model = ins_open_factory.create(
        receiver=signature_model.owner,
        routing="/node/register/verify",
        data={"v": ok_base64},
        res=signature_ins_model.bid,
    )
    # 发送指令
    await execute_send_ins(ins=ok_send_ins_model, is_res=False)

    # --------------- 节点创建
    node_model = NodeModel(bid=signature_model.owner, websocket=None, signature_model=signature_model, encryption_key=encryption_key)
    NodeManager().active_node.update({signature_model.owner: node_model})

    # ----------------------- 保存证书
    save_to_yaml(node_model.signature_model.data, f"./data/signature/{node_model.signature_model.bid}.yml")

    return node_model


