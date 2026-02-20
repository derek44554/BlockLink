import os

from starlette.websockets import WebSocket
from websockets import ClientConnection

from blocklink.models.signature.signature import SignatureModel
from blocklink.utils.cryptography import decrypt_with_symmetric_key_base64, encrypt_with_symmetric_key_base64

"""
节点
"""


class NodeModel:
    def __init__(
            self,
            bid: str,
            websocket: WebSocket | ClientConnection | None,
            signature_model: SignatureModel,
            encryption_key,

    ):
        self.bid = bid
        self.websocket: WebSocket | ClientConnection | None = websocket
        self.signature_model = signature_model  # 签名
        self.encryption_key: bytes = encryption_key  # 用于加密的Key os.urandom(32)
        self.info = {}  # 节点信息

    async def send_text(self, text):
        """
        发送消息
        :param text:
        :return:
        """
        if type(self.websocket) == WebSocket:
            await self.websocket.send_text(text)
        elif type(self.websocket) == ClientConnection:
            await self.websocket.send(text)
        else:
            ...

    def encryption_base64(self, data: bytes):
        """
        对称加密
        :param data:
        :return:
        """
        # 加密数据
        encrypting_data = encrypt_with_symmetric_key_base64(key=self.encryption_key, data=data)

        return encrypting_data

    def decrypt_base64(self, data: str):
        """
        解密
        :param data:
        :return:
        """
        decrypt_data = decrypt_with_symmetric_key_base64(key=self.encryption_key, encrypted_base64=data)
        return decrypt_data
