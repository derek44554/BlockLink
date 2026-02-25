from blocklink.utils.cryptography import public_key_to_pem, load_private_key, public_key_to_binary

from blocklink.utils.tools import generate_bid, get_datetime_after_days, save_dict_to_yaml
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
import base64

from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes


"""
生成密钥对
"""

def generate_and_save_rsa_keys(path=""):
    """
    生成密钥对
    :param path: 保存的路径
    :return:
    """
    # 确保路径以 / 结尾
    if path and not path.endswith("/"):
        path += "/"
    
    # 生成RSA私钥
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=4096,
        backend=default_backend()
    )

    # 获取对应的公钥
    public_key = private_key.public_key()

    # 将私钥保存到文件（无加密）
    with open(f"{path}private_key_top.pem", "wb") as f:
        f.write(
            private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption()
            )
        )

    # 将公钥保存到文件
    with open(f"{path}public_key_top.pem", "wb") as f:
        f.write(
            public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
        )


def generate_node(
        private_key_top_path="private_key_top.pem",
        output_dir="node",
        permission_level=1,
        validity_days=365
):
    """
    生成节点及其签名证书
    
    该函数用于创建一个新的授权节点，完整流程包括：
    1. 生成节点的 RSA 密钥对（4096位私钥和公钥）
    2. 创建节点证书（signature.yml），证书中包含节点公钥
    3. 使用顶级私钥对证书进行签名，证明该节点是被授权的
    4. 保存节点密钥对、证书和节点信息
    
    工作原理（类似 PKI 证书体系）：
    - 顶级私钥作为证书颁发机构（CA）的私钥，用于签发节点证书
    - 节点证书（signature.yml）包含：节点公钥、权限等级、有效期、顶级私钥的签名
    - 节点私钥（private_key.pem）由节点持有，用于解密其他节点发送的加密数据
    
    节点间验证流程：
    1. 节点A获取节点B的证书（signature.yml）
    2. 节点A使用顶级公钥验证证书上的签名
    3. 验证通过后，节点A信任节点B，并使用证书中的公钥加密数据发送给节点B
    4. 节点B使用自己的私钥（private_key.pem）解密数据

    参数说明:
        private_key_top_path (str): 顶级签名私钥文件路径（必填）
            - 用于签名授权的顶级私钥文件（证书颁发机构的私钥）
            - 该私钥拥有签发节点证书的权限
            - 对应的顶级公钥需要分发给所有节点用于验证证书
            - 例如: "keys/private_key_top.pem"

        output_dir (str): 输出目录，默认为"node"
            - 生成的文件都会保存到此目录：
              * signature.yml - 节点证书（包含节点公钥和顶级私钥的签名）
              * public_key.pem - 节点公钥（与证书中的公钥对应）
              * private_key.pem - 节点私钥（用于解密数据，需妥善保管）
              * node.yml - 节点基本信息（节点ID等）
            - 例如: "output/nodes"

        permission_level (int): 权限等级，默认为1
            - 定义节点在网络中的权限级别
            - 1: 普通权限
            - 2: 中级权限
            - 3: 高级权限

        validity_days (int): 证书有效天数，默认为365天
            - 从当前日期开始计算的证书有效期
            - 过期后证书需要重新签发

    返回值:
        tuple: (node_data, signature_data)
            - node_data: 节点数据字典（包含节点ID等信息）
            - signature_data: 签名证书数据字典（包含公钥、签名、权限等）

    异常:
        FileNotFoundError: 当顶级私钥文件不存在时抛出
        ValueError: 当参数值不合法时抛出
        OSError: 当无法创建输出目录或写入文件时抛出

    示例:
        # 基本使用 - 生成普通权限节点
        node, signature = generate_node(
            private_key_top_path="keys/private_key_top.pem",
            output_dir="output/node1"
        )

        # 生成高权限节点，有效期180天
        node, signature = generate_node(
            private_key_top_path="keys/private_key_top.pem",
            output_dir="output/admin_node",
            permission_level=3,
            validity_days=180
        )
        
    注意事项:
        - 节点私钥（private_key.pem）必须妥善保管，不能泄露
        - 顶级私钥（private_key_top_path）权限极高，需要严格保护
        - 所有节点需要持有顶级公钥（public_key_top.pem）才能验证证书
        - 证书过期后节点将无法通过验证，需要重新生成
    """

    # ----------------------
    # 1. 初始化节点数据
    # ----------------------
    node_data = {
        "bid": generate_bid(),  # 生成唯一的节点ID
        "model": "node",  # 数据模型类型
    }

    # ----------------------
    # 2. 初始化签名数据结构
    # ----------------------
    signature_data = {
        "bid": generate_bid(),  # 生成唯一的签名ID
        "model": "signature",  # 数据模型类型
        "signature": "",  # 签名数据（稍后填充）
        "owner": node_data["bid"],  # 签名所属的节点ID
        "permission_level": permission_level,  # 权限等级
        "validity_period": "",  # 有效期（稍后填充）
        "public_key_pem": "",  # 公钥PEM格式（稍后填充）
    }

    # ----------------------
    # 3. 计算有效期
    # ----------------------
    # 根据输入的天数计算未来的日期时间
    validity_period = get_datetime_after_days(validity_days)
    signature_data["validity_period"] = validity_period

    # ----------------------
    # 4. 生成节点的 RSA 密钥对
    # ----------------------
    # 生成 RSA 私钥
    node_private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=4096,
        backend=default_backend()
    )
    # 从私钥获取对应的公钥
    node_public_key = node_private_key.public_key()
    
    # 将公钥转换为PEM格式字符串并保存到签名数据中
    signature_data["public_key_pem"] = public_key_to_pem(node_public_key)

    # ----------------------
    # 5. 加载顶级签名私钥
    # ----------------------
    # 从文件加载用于签名的顶级私钥
    top_sign_key = load_private_key(private_key_top_path)

    # ----------------------
    # 6. 构建待签名消息
    # ----------------------
    # 按照特定格式组装待签名的消息
    # 格式: 节点BID + 空格 + 权限等级(2字节) + 空格 + 有效期 + 空格 + 公钥二进制
    message_prefix = node_data["bid"].encode('utf-8')  # 节点BID转为字节
    message_prefix += b" "  # 分隔符
    message_prefix += permission_level.to_bytes(2, byteorder='big')  # 权限等级转为2字节大端序
    message_prefix += b" "  # 分隔符
    message_prefix += validity_period.encode('utf-8')  # 有效期转为字节
    message_prefix += b" "  # 分隔符
    message_prefix += public_key_to_binary(node_public_key)  # 公钥转为二进制格式

    # ----------------------
    # 7. 使用私钥对消息进行签名
    # ----------------------
    # 使用PSS填充方案和SHA3-256哈希算法进行签名
    signature = top_sign_key.sign(
        message_prefix,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA3_256()),  # 掩码生成函数使用SHA3-256
            salt_length=padding.PSS.MAX_LENGTH  # 使用最大盐长度
        ),
        hashes.SHA3_256()  # 哈希算法
    )

    # 将签名转换为Base64编码的ASCII字符串，便于存储和传输
    base64_signature = base64.b64encode(signature).decode('ascii')
    signature_data["signature"] = base64_signature

    # ----------------------
    # 8. 保存数据到文件
    # ----------------------
    # 确保输出目录存在
    import os
    os.makedirs(output_dir, exist_ok=True)
    
    # 构建输出文件的完整路径
    node_output_path = f"{output_dir}/node.yml"
    signature_output_path = f"{output_dir}/signature.yml"
    node_private_key_path = f"{output_dir}/private_key.pem"
    node_public_key_path = f"{output_dir}/public_key.pem"

    # 将节点数据保存为YAML格式
    save_dict_to_yaml(node_data, node_output_path)
    # 将签名数据保存为YAML格式
    save_dict_to_yaml(signature_data, signature_output_path)
    
    # 保存节点私钥到文件（无加密）
    with open(node_private_key_path, "wb") as f:
        f.write(
            node_private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption()
            )
        )
    
    # 保存节点公钥到文件
    with open(node_public_key_path, "wb") as f:
        f.write(
            node_public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
        )

    # 返回生成的数据
    return node_data, signature_data
