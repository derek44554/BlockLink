import hashlib
import os
from datetime import datetime, timezone
from cryptography.hazmat.primitives import padding as sym_padding
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes
import base64
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

"""
密码学加密工具
"""


def load_private_key(path, password=None):
    """从文件加载私钥"""
    with open(path, "rb") as f:
        private_pem = f.read()
    private_key = serialization.load_pem_private_key(
        private_pem,
        password=password,  # 如果有密码保护则提供密码，否则None
        backend=default_backend()
    )
    return private_key

def load_public_key(path):
    """从文件加载公钥"""
    with open(path, "rb") as f:
        public_pem = f.read()
    public_key = serialization.load_pem_public_key(
        public_pem,
        backend=default_backend()
    )
    return public_key

def load_pem_to_public_key(pem_data: str):
    """
    将PEM格式的公钥转换为公钥对象
    参数:
        pem_data: PEM格式的公钥字符串
    返回:
        公钥对象
    """
    public_key = serialization.load_pem_public_key(
        pem_data.encode('utf-8')
    )
    return public_key

def public_key_to_binary(public_key) -> bytes:
    """
    将公钥对象转换为二进制格式(DER编码)
    参数:
        public_key: 公钥对象
    返回:
        二进制格式的公钥(bytes)
    """
    binary_key = public_key.public_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    return binary_key


def encrypt_with_public_key_base64(public_key, data_bytes):
    """
    使用公钥加密数据
    :param public_key:
    :param data_bytes:
    :return: base64
    """
    # 将数据转换为字节
    # data_bytes = data.encode('utf-8')

    # 使用OAEP填充方案加密
    encrypted_data = public_key.encrypt(
        data_bytes,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),  # 掩码生成函数
            algorithm=hashes.SHA256(),  # 哈希算法
            label=None  # 可选标签，通常为None
        )
    )

    # 将加密结果转为base64
    encrypted_base64 = base64.b64encode(encrypted_data).decode('utf-8')
    return encrypted_base64


def decrypt_with_private_key_base64(private_key, encrypted_base64):
    """
    使用私钥解密数据
    参数:
        private_key: 私钥对象
        encrypted_base64: Base64编码的加密数据字符串
    返回:
        解密后的数据（字节形式）
    """
    # 将base64编码的字符串解码为字节
    encrypted_bytes = base64.b64decode(encrypted_base64)

    # 使用私钥解密
    decrypted_data = private_key.decrypt(
        encrypted_bytes,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),  # 掩码生成函数
            algorithm=hashes.SHA256(),  # 哈希算法
            label=None  # 可选标签，通常为None
        )
    )

    return decrypted_data

# 自定义转换函数，将 datetime 对象转为 ISO 8601 格式的字符串（带 Z）
def datetime_converter(obj):
    if isinstance(obj, datetime):
        # 将时间转换为 UTC（确保时区为 UTC）
        obj = obj.replace(tzinfo=timezone.utc) if obj.tzinfo is None else obj.astimezone(timezone.utc)
        return obj.strftime('%Y-%m-%dT%H:%M:%SZ')  # 以 ISO 8601 格式返回


def encrypt_with_symmetric_key_base64(key, data: bytes):
    """
    使用对称密钥加密数据
    :param key: 对称密钥（需要是 16、24 或 32 字节的长度）
    :param data: 待加密的数据字节
    :return: base64编码的加密数据
    """
    # 生成一个随机初始化向量（IV）
    iv = os.urandom(16)

    # 创建 AES-CBC 加密器
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()

    # 对数据进行 PKCS7 填充
    padder = sym_padding.PKCS7(128).padder()  # 128 位 = 16 字节块大小
    padded_data = padder.update(data) + padder.finalize()

    # 加密
    encrypted_data = encryptor.update(padded_data) + encryptor.finalize()

    # 返回加密后的数据与初始化向量（IV），两者都进行 base64 编码
    encrypted_base64 = base64.b64encode(iv + encrypted_data).decode('utf-8')
    return encrypted_base64


def decrypt_with_symmetric_key_base64(key, encrypted_base64):
    """
    使用对称密钥解密数据
    :param key: 对称密钥（需要是 16、24 或 32 字节的长度）
    :param encrypted_base64: base64 编码的加密数据（包括 IV 和密文）
    :return: 解密后的原始数据（字节形式）
    """
    # 将 base64 编码的加密数据解码为字节
    encrypted_data_with_iv = base64.b64decode(encrypted_base64)

    # 分离出初始化向量（IV）和密文
    iv = encrypted_data_with_iv[:16]  # 前 16 字节为 IV
    encrypted_data = encrypted_data_with_iv[16:]  # 后面的部分是加密数据

    # 使用 AES 算法解密数据（CBC模式）
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    decrypted_padded_data = decryptor.update(encrypted_data) + decryptor.finalize()

    # 移除 PKCS7 填充
    unpadder = sym_padding.PKCS7(128).unpadder()  # 128 位 = 16 字节块大小
    decrypted_data = unpadder.update(decrypted_padded_data) + unpadder.finalize()

    return decrypted_data

def public_key_to_pem(public_key) -> str:
    """
    将 RSAPublicKey 对象序列化为 PEM 格式的字符串。
    """
    pem_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    return pem_bytes.decode('utf-8')


def get_file_sha3_256(file_path):
    sha3 = hashlib.sha3_256()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            sha3.update(chunk)
    return sha3.hexdigest()

