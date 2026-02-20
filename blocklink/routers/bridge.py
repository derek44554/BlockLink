import json
import os
import base64
import binascii

from fastapi import APIRouter, Body, HTTPException, Request

from blocklink.models.ins.ins_open_factory import InsOpenFactory
from blocklink.models.ins.ins_cert_factory import INS_CERT_FACTORY
from blocklink.utils.model.bridge_res import BridgeRes
from fastapi.encoders import jsonable_encoder

from blocklink.utils.cryptography import decrypt_with_symmetric_key_base64, encrypt_with_symmetric_key_base64
from blocklink.utils.send import execute_send_ins

bridge_api = APIRouter()


@bridge_api.post(
    "/ins",
    summary="HTTP -> 指令桥接入口",
    description="将HTTP请求转换为框架指令（open/cert），自动选择本地处理或网络转发，并可等待回复。",
    status_code=200,
)
async def bridge_ins(
        request: Request,
        text: str = Body(..., embed=True),
):
    """统一HTTP桥接：
    - text: 经过对称加密的指令 JSON 文本（base64）
    """
    identity_base64 = os.getenv("IDENTITY")
    if not identity_base64:
        raise HTTPException(status_code=500, detail="IDENTITY is not configured")

    try:
        key = base64.b64decode(identity_base64)
    except (binascii.Error, ValueError) as exc:
        raise HTTPException(status_code=500, detail="IDENTITY is invalid base64") from exc

    try:
        decrypted_bytes = decrypt_with_symmetric_key_base64(key, text)
    except Exception as exc:  # pragma: no cover - 保留详细异常信息
        raise HTTPException(status_code=400, detail="failed to decrypt payload") from exc

    try:
        payload = json.loads(decrypted_bytes.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise HTTPException(status_code=400, detail="payload is not valid JSON") from exc

    protocol = payload.get("protocol", payload.get("protoco"))
    routing = payload.get("routing")
    data = payload.get("data")
    receiver = payload.get("receiver")
    wait = payload.get("wait", False)
    timeout = payload.get("timeout", 60)

    if routing is None:
        raise HTTPException(status_code=400, detail="routing is required")

    if protocol not in ("open", "cert"):
        raise HTTPException(status_code=400, detail="unsupported protocol")

    if isinstance(wait, str):
        wait_lower = wait.lower()
        if wait_lower in ("true", "1"):
            wait = True
        elif wait_lower in ("false", "0"):
            wait = False
        else:
            raise HTTPException(status_code=400, detail="wait is invalid")
    elif not isinstance(wait, bool):
        wait = bool(wait)

    try:
        timeout_value = int(timeout)
    except (TypeError, ValueError):
        raise HTTPException(status_code=400, detail="timeout must be an integer")

    if protocol == "open":
        ins_open_factory = InsOpenFactory()
        ins = ins_open_factory.create(receiver=receiver, routing=routing, data=data)
    elif protocol == "cert":
        ins = INS_CERT_FACTORY.create(receiver=receiver, routing=routing, data=data)
    else:
        raise
    ins_res = await execute_send_ins(ins=ins, is_res=wait, timeout=timeout_value)

    bridge_res = BridgeRes(bid=ins_res.bid, status_code=ins_res.status_code, data=ins_res.data, sender=ins_res.sender, res=ins_res.res)

    try:
        response_payload = jsonable_encoder(bridge_res.dict)
        response_bytes = json.dumps(response_payload, ensure_ascii=False).encode("utf-8")
        encrypted_text = encrypt_with_symmetric_key_base64(key, response_bytes)
    except Exception as exc:  # pragma: no cover - 保留详细异常信息
        raise HTTPException(status_code=500, detail="failed to encrypt response") from exc

    return {"text": encrypted_text}
