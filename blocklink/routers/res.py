from blocklink.utils.res_futures import ResFutures

from blocklink.models.node.node import NodeModel
from blocklink.models.routers.route_block import RouteBlock
from starlette.websockets import WebSocket
from blocklink.models.ins.ins_cert import InsCert
from blocklink.models.ins.ins_open import InsOpen

res_route = RouteBlock(route="/res")


@res_route.open("/data")
async def open_res_data(websocket: WebSocket, ins_open: InsOpen):
    """
    指令接收 一般用于接收返回数据的
    :param websocket:
    :param ins_open:
    :return:
    """
    ResFutures().res_ins(ins_open)

@res_route.cert("/data")
async def cert_res_data(node_model: NodeModel, ins_cert: InsCert):
    """
    指令接收 一般用于接收返回数据的
    :param node_model:
    :param ins_cert:
    :return:
    """
    ResFutures().res_ins(ins_cert)


@res_route.cert("/file")
async def res_file(node_model: NodeModel, ins_cert: InsCert):
    """
    指令接收 接收一个文件
    :param node_model:
    :param ins_cert:
    :return:
    """
    ResFutures().res_file(ins_cert)

