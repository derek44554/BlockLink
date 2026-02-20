import asyncio

from blocklink.utils.model.ins_record import InsRecord

from blocklink.utils.res_futures import ResFutures
from starlette.websockets import WebSocket
from blocklink.models.ins.ins_cert import InsCert
from blocklink.models.ins.ins_open import InsOpen
from blocklink.utils.ins_except import InsException, InsOpenException
from blocklink.utils.node_send import node_send_v2
from websockets import ClientConnection

"""
高级发送封装

找到对应发送的Node
如果没有直接连接的Node 会决定用哪个Node来发送
"""


async def execute_send_ins(ins: InsOpen | InsCert, is_res=False, timeout=60, websocket=None):
    """
    forward 为继续处理
    """
    # 本地直达：若接收者是本节点，则不经网络转发，直接进入本地路由处理
    from blocklink.utils.node_meta import NodeMeta
    from blocklink.models.routers.route_block_manage import ROUTE_BLOCK_MANAGE

    # 如果需要跳过 则不进行处理
    if InsRecord().is_skip(ins):
        return None

    # 添加指令的BID记录
    InsRecord().add_ins(ins)

    #  -------------------------------- 接收者是本节点
    if ins.receiver == NodeMeta()["bid"] or ins.receiver == NodeMeta()["bid"][:10] or ins.receiver == "":
        # 本地处理分支
        # 为保证本地同步返回不会抢跑，先注册 future 再进入 handler
        future = None
        if is_res:
            future = ResFutures().add_ins(ins)

        try:
            # 执行路由处理函数
            await ROUTE_BLOCK_MANAGE.get_handler(websocket=websocket, ins=ins)
        except InsOpenException as e:
            # 如果指令的接收者是* 并且状态码为41找不到对应的处理路由 则进行转发
            if e.status_code == 41:
                print(f"找不到对应路由 {e.ins_open.routing}")
                return None
            else:
                raise e

        if not is_res:
            return None

        # 等待本地结果
        response = await asyncio.wait_for(future, timeout=timeout)
        return response

    # 远端发送：选择节点并通过 websocket 发送
    await node_send_v2(ins.receiver, data=ins.text)

    # 是否 不需要返回数据
    if not is_res:
        # 直接返回
        return None

    # 注册指令（远端发送时，网络往返足够保证注册先于响应到达）
    future = ResFutures().add_ins(ins)

    # 等待指令返回结果
    response = await asyncio.wait_for(future, timeout=timeout)

    return response

