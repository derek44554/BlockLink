import os
from starlette.websockets import WebSocket
from blocklink.adapters.ins.node import send_ins_node_info
from blocklink.models.connect.connect import ConnectModel
from blocklink.models.connect.connect_manager import ConnectManager
from blocklink.models.ins.ins_cert import InsCert
from blocklink.models.ins.ins_open import InsOpen
from blocklink.models.node.node import NodeModel
from blocklink.models.node.node_manager import NodeManager
from blocklink.models.routers.route_block import RouteBlock
from blocklink.models.signature.signature import SignatureModel
from blocklink.utils.ins_except import InsException
from blocklink.utils.node_meta import NodeMeta
from blocklink.utils.cryptography import decrypt_with_private_key_base64, encrypt_with_public_key_base64, \
    decrypt_with_symmetric_key_base64
from websockets import ClientConnection
from blocklink.utils.tools import save_to_yaml

node_route = RouteBlock(route="/node")


@node_route.open("/signature")
async def node_signature(websocket: WebSocket | ClientConnection, ins_open: InsOpen):
    """
    获取签名
    :param websocket:
    :param ins_open:
    :return:
    """
    return NodeMeta().signature


@node_route.open("/node")
async def node_data(websocket: WebSocket | ClientConnection, ins_open: InsOpen):
    """
    获取节点信息
    :param websocket:
    :param ins_open:
    :return:
    """
    return NodeMeta().node


@node_route.open("/register/start")
async def node_start(websocket: WebSocket | ClientConnection, ins_open: InsOpen):
    # -------------------- 签名
    # 随机挑战 密文
    challenge_ciphertext = ins_open.data["challenge"]

    # 签名
    signature = ins_open.data["signature"]

    # 创建签名对象
    signature_model = SignatureModel(data=signature, **signature)

    # 是否 此BID已经注册 并且是存在 websocket
    if NodeManager().is_active(signature_model.owner, is_connect=True):
        # 保险起建 通过NodeManager()进行一次断开连接
        NodeManager().disconnect(websocket)
        await websocket.close()  # 使用正常关闭码
        raise InsException(ins=ins_open, status_code=53)

    # 签名是否合法
    is_verify = signature_model.is_verify
    if is_verify is False:
        raise ValueError("Invalid signature verification")

    # -------------------- 创建未注册的节点
    node_model = NodeModel(bid=signature_model.owner, websocket=websocket, signature_model=signature_model,
                           encryption_key=os.urandom(32))
    # 存放未激活节点
    NodeManager().not_active(node_model)

    # 随机挑战 解密
    challenge_decryption = decrypt_with_private_key_base64(private_key=NodeMeta().node_private_pey,
                                                           encrypted_base64=challenge_ciphertext)

    # 随机挑战值
    challenge_key = challenge_decryption[:32]
    # 随机挑战发布者
    publisher = str(challenge_decryption[32:], encoding='utf-8')

    # 需要验证发布者与对面节点是否相同
    if publisher != signature_model.owner:
        raise

    # 使用对方公钥将 随机挑战 与 生成的对称加密密钥 一同加密发挥
    ciphertext_data = encrypt_with_public_key_base64(public_key=signature_model.public_key,
                                                     data_bytes=challenge_key + node_model.encryption_key)

    return {"v": ciphertext_data}


@node_route.open("/register/verify")
async def node_verify(websocket: WebSocket | ClientConnection, ins_open: InsOpen):
    # 发送者BID
    sender = ins_open.sender
    # 密文数据
    ciphertext_data = ins_open.data["v"]

    # 未注册节点
    node_model = NodeManager().not_active_node[sender]

    # 通过节点的 对称加密 进行解密
    # 是否可以解密出ok
    decryption_results = decrypt_with_symmetric_key_base64(key=node_model.encryption_key,
                                                           encrypted_base64=ciphertext_data)

    # 是否认证不通过
    if decryption_results != b'ok':
        raise

    # 将节点进行注册
    NodeManager().active(node_model)

    # ----------------------- 保存证书
    save_to_yaml(node_model.signature_model.data, f"./data/signature/{node_model.signature_model.bid}.yml")

    # ----------------------- 保存连接信息
    connect_data = {
        "bid": node_model.bid,
        "public_address": None,
        "private_address": None,
        "mac": None,
        "key_hex": node_model.encryption_key.hex(),
    }
    connect_model = ConnectModel(data=connect_data)
    connect_model.save()
    # 将 connect_model 统一管理
    ConnectManager().add(connect_model)

    # ----------------------- 发送节点信息
    await send_ins_node_info(node_model.bid)
    print(f"接收连接 {node_model.bid}")


@node_route.cert("/res_info")
async def res_info(node_model: NodeModel, ins_cert: InsCert):
    """
    接收其他节点信息
    用于知道对方配置 如是否为转发节点
    """
    # 是否 接收的数据不为字典
    if not isinstance(ins_cert.data, dict):
        raise
    node_model.info = ins_cert.data

