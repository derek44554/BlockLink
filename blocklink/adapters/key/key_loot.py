from blocklink.utils.cryptography import load_public_key, public_key_to_pem, load_private_key, public_key_to_binary

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
    # 生成RSA私钥
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=4096,
        backend=default_backend()
    )

    # 获取对应的公钥
    public_key = private_key.public_key()

    # 将私钥保存到文件（无加密）
    with open(f"{path}private_key.pem", "wb") as f:
        f.write(
            private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption()
            )
        )

    # 将公钥保存到文件
    with open(f"{path}public_key.pem", "wb") as f:
        f.write(
            public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
        )


def generate_node(
        node_public_key_path,
        top_sign_key_path,
        output_dir="node",
        permission_level=1,
        validity_days=365
):
    """
    生成节点及其签名数据

    参数说明:
        node_public_key_path (str): 节点公钥文件路径（必填）
            - 指向节点公钥文件的完整路径
            - 例如: "keys/public_key.pem"

        top_sign_key_path (str): 顶级签名私钥文件路径（必填）
            - 用于签名的顶级私钥文件完整路径
            - 例如: "keys/private_key.pem"

        output_dir (str): 输出目录（必填）
            - 生成的node.yml和signature.yml都会保存到此目录
            - 例如: "output/nodes"

        permission_level (int): 权限等级，默认为1
            - 1: 普通权限
            - 2: 中级权限
            - 3: 高级权限

        validity_days (int): 有效天数，默认为365天
            - 从当前日期开始计算的有效期天数

    返回值:
        tuple: (node_data, signature_data)
            - node_data: 节点数据字典
            - signature_data: 签名数据字典

    异常:
        FileNotFoundError: 当公钥或私钥文件不存在时抛出
        ValueError: 当参数值不合法时抛出

    示例:
        # 基本使用
        node, signature = generate_node(
            node_public_key_path="keys/public_key.pem",
            top_sign_key_path="keys/private_key.pem",
            output_dir="output"
        )

        # 自定义权限和有效期
        node, signature = generate_node(
            node_public_key_path="keys/public_key.pem",
            top_sign_key_path="keys/private_key.pem",
            output_dir="output",
            permission_level=2,
            validity_days=180
        )
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
    # 4. 加载并处理节点公钥
    # ----------------------
    # 从文件加载节点的公钥
    node_public_key = load_public_key(node_public_key_path)
    # 将公钥转换为PEM格式字符串并保存到签名数据中
    signature_data["public_key_pem"] = public_key_to_pem(node_public_key)

    # ----------------------
    # 5. 加载顶级签名私钥
    # ----------------------
    # 从文件加载用于签名的顶级私钥
    top_sign_key = load_private_key(top_sign_key_path)

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
    # 构建输出文件的完整路径
    node_output_path = f"{output_dir}/node.yml"
    signature_output_path = f"{output_dir}/signature.yml"

    # 将节点数据保存为YAML格式
    save_dict_to_yaml(node_data, node_output_path)
    # 将签名数据保存为YAML格式
    save_dict_to_yaml(signature_data, signature_output_path)

    # 返回生成的数据
    return node_data, signature_data
