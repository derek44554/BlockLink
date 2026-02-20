import requests
import os
import tempfile
from pathlib import Path

from Crypto.Cipher import AES

def encrypt_file(file_path: str, key: bytes) -> str:
    """加密文件并返回加密后的临时文件路径（跨平台适配）"""
    # 使用系统临时目录，并随机生成文件名
    tmp_dir = Path(tempfile.gettempdir())
    encrypted_file_path = tmp_dir / f"{os.urandom(16).hex()}"

    nonce = os.urandom(16)  # 128-bit nonce
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)

    with open(file_path, "rb") as file:
        file_data = file.read()

    ciphertext, tag = cipher.encrypt_and_digest(file_data)

    with open(encrypted_file_path, "wb") as enc_file:
        enc_file.write(nonce)
        enc_file.write(tag)
        enc_file.write(ciphertext)

    return str(encrypted_file_path)




def upload_file_ipfs(file_path: str, address: str) -> str:
    """调用 FastAPI 接口上传文件并返回 CID。"""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"文件不存在: {file_path}")

    with path.open("rb") as fh:
        files = {"file": (path.name, fh)}
        data = {"password": "dirrk2938884jMMFhs01"}
        response = requests.post(f"{address}/ipfs/ipfs/upload", data=data, files=files)
        response.raise_for_status()
        return response.json()["cid"]