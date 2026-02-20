import base64

from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.exceptions import InvalidSignature

from blocklink.utils.node_meta import NodeMeta


def signature_verify(signature_base64, data) -> bool:
    """
    签名验证
    :param signature_base64:
    :param data:
    :return:
    """
    # 将 Base64 签名解码为二进制
    signature = base64.b64decode(signature_base64)

    # 验证签名
    try:
        NodeMeta().top_verify_public_pey.verify(
            signature,
            data,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA3_256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA3_256()
        )
        return True
    except InvalidSignature:
        return False