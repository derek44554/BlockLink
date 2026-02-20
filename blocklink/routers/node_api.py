import json
from fastapi import Response
from fastapi import APIRouter

from blocklink.utils.cryptography import datetime_converter
from blocklink.utils.node_meta import NODE_MEAT

node_api = APIRouter()

@node_api.get("/signature", summary='获取签名')
async def get_signature():
    """
    获取签名
    """
    data = json.dumps(NODE_MEAT.signature, indent=4, default=datetime_converter)
    return Response(content=data, media_type='application/json')
