import asyncio
import base64

from blocklink.models.ins.factory import Ins
from blocklink.models.ins.ins_cert import InsCert
from blocklink.models.ins.ins_open import InsOpen
from blocklink.utils.singleton_meta import SingletonMeta

"""
数据池
请求其他节点后返回回来的数据
"""


class ResFutures(metaclass=SingletonMeta):
    def __init__(self):
        self.ins_data = {}
        # {"请求的BID": {"future": future, "count": 3, "data": {0: 数据块, 1:数据块} }}
        self.file_data = {}

    def add_ins(self, ins: Ins):
        future = asyncio.get_event_loop().create_future()
        # 用于激活异步函数
        self.ins_data[ins.bid] = future
        return future

    def res_ins(self, ins: Ins):
        # 用于激活异步函数
        future = self.ins_data.get(ins.res, None)
        # 是否 垃圾响应
        if future is None:
            print(f"垃圾响应 open {ins.bid} {ins.res}")
            return None
        future.set_result(ins)

    def add_file(self, ins_cert: InsCert):
        """
        请求接收文件
        :param ins_cert:
        :return:
        """
        future = asyncio.get_event_loop().create_future()
        # 用于激活异步函数
        self.file_data[ins_cert.bid] = {"future": future, "count": 0, "data": {}}
        return future

    def res_file(self, ins_cert: InsCert):
        file_obj = self.file_data.get(ins_cert.res, None)
        # 是否 垃圾响应
        if file_obj is None:
            print(f"垃圾响应 cert 文件 {ins_cert.bid} {ins_cert.res}")
            return None

        # --------------------- 块注入
        # 全部块数量
        count = ins_cert.data["count"]
        file_obj["count"] = count
        # 索引
        index = ins_cert.data["index"]
        # 此索引接收数据
        file_obj["data"][index] = ins_cert.data["data"]

        # 是否没有接收完成
        if file_obj["count"] != len(file_obj["data"]):
            return None
        # --------------------- 全部接收完成
        # 合并所有块并解码base64数据
        complete_file_data = b""
        for i in range(count):
            chunk_base64 = file_obj["data"][i]
            chunk_data = base64.b64decode(chunk_base64)  # 解码base64到字节
            complete_file_data += chunk_data  # 组合数据块

        # --------------------- 用于激活异步函数
        file_obj = self.file_data[ins_cert.res]
        future = file_obj["future"]
        future.set_result(complete_file_data)

        # --------------------- 清理内存
        del self.file_data[ins_cert.res]

