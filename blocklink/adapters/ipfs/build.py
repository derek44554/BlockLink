import os
from blocklink.adapters.ipfs.tools import encrypt_file, upload_file_ipfs
from blocklink.utils.cryptography import get_file_sha3_256

def build_ipfs_http(file_path, address, ) -> dict:
    """构建IPFS 文件"""
    # 文件扩展名
    ext = os.path.splitext(file_path)[1]
    # 文件大小
    file_size = os.path.getsize(file_path)
    # 文件SHA3-256
    sha3_256 = get_file_sha3_256(file_path)

    # 上传
    cid =  upload_file_ipfs(file_path=file_path, address=address)

    ipfs = {
        "cid": cid,
        "ext": ext,
        "size": file_size,
        "sha3_256": sha3_256,
    }

    return ipfs


def build_ipfs_http_encrypted(file_path, address) -> dict:
    """构建IPFS 加密文件"""
    key = os.urandom(32)  # 加密Key
    # 加密文件
    # 返回路径
    encrypted_file_path = encrypt_file(file_path=file_path, key=key)

    # 文件扩展名
    ext = os.path.splitext(file_path)[1]

    # 文件大小 加密后的
    file_size = os.path.getsize(encrypted_file_path)
    # 文件SHA3-256
    sha3_256 = get_file_sha3_256(encrypted_file_path)

    # 上传
    cid =  upload_file_ipfs(file_path=encrypted_file_path, address=address)

    # ------------------------ 删除临时文件
    if os.path.exists(encrypted_file_path):
        os.remove(encrypted_file_path)

    ipfs = {
        "cid": cid,
        "ext": ext,
        "size": file_size,
        "sha3_256": sha3_256,
        "encryption": {"algo": "PPE-001", "key": key.hex()}
    }

    return ipfs

