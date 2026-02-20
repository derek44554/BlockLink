from typing import Any

from blocklink.utils.api import bridge_request
from blocklink.utils.block_model import BlockModel
from blocklink.utils.model.bridge_res import BridgeRes


def get_open_block(bid: str, receiver="*") -> BlockModel:
    data = {"bid": bid}
    request = bridge_request(protocol="open", routing="/block/block/get", data=data, receiver=receiver)

    block_model = BlockModel(data=request.json()["data"])
    return block_model


def get_block(bid: str, receiver="") -> BlockModel:
    data = {"bid": bid}
    request = bridge_request(protocol="cert", routing="/block/block/get", data=data, receiver=receiver)

    bridge_res = BridgeRes(**request.json())
    block_model = BlockModel(data=bridge_res.data)

    return block_model


def block_multiple(bids: str, receiver="") -> tuple[list[Any], list[Any]]:
    data = {"bids": bids}
    request = bridge_request(protocol="cert", routing="/block/block/multiple", data=data, receiver=receiver)
    deny_bids = request.json()["deny_bids"]

    blocks = []
    for block_data in request.json()["data"]["blocks"]:
        block_model = BlockModel(data=block_data)
        blocks.append(block_model)

    return blocks, deny_bids
