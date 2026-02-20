
from blocklink.utils.api import bridge_request
from blocklink.utils.block_model import BlockModel
from blocklink.utils.model.block_page_model import BlockPageModel


def link_target_count(bid, receiver="") -> int:
    data = {"bid": bid}
    request = bridge_request(protocol="cert", routing="/block/link/target/count", data=data, receiver=receiver)

    count = request.json()["data"]["count"]
    return count

def link_main_count(bid, receiver="") -> int:
    data = {"bid": bid}
    request = bridge_request(protocol="cert", routing="/block/link/main/count", data=data, receiver=receiver)

    count = request.json()["data"]["count"]
    return count


def link_target_multiple(bid, page, receiver="") -> BlockPageModel:
    data = {"bid": bid, "page": page}
    request = bridge_request(protocol="cert", routing="/block/link/target/multiple", data=data, receiver=receiver)


    return BlockPageModel.from_dict(request.json()["data"])


def link_main_multiple(bid, page, receiver="") -> BlockPageModel:
    data = {"bid": bid, "page": page}
    request = bridge_request(protocol="cert", routing="/block/link/main/multiple", data=data, receiver=receiver)

    return BlockPageModel.from_dict(request.json()["data"])