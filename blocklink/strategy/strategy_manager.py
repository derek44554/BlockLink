import asyncio
from typing import List
from contextlib import asynccontextmanager

from fastapi import FastAPI

from blocklink.strategy.strategy import Strategy


class StrategyManager:
    def __init__(self):
        self.strategies: List[Strategy] = []
        self.functions = []  # 需要运行的函数列表

    def add(self, strategy: Strategy):
        """添加启动时执行的策略"""
        self.strategies.append(strategy)

    def add_function(self, function):
        """项目启动时运行的一些函数"""
        self.functions.append(function)

    async def run_all(self):
        """并行运行所有启动策略和函数"""
        # 启动所有策略
        tasks = [strategy.run() for strategy in self.strategies]

        # 启动所有函数
        function_tasks = [function() for function in self.functions]

        # 并行运行所有任务
        await asyncio.gather(*tasks, *function_tasks)  # 并行执行所有策略和函数

    @asynccontextmanager
    async def lifespan(self, app: FastAPI):
        """Lifespan context manager for managing startup and shutdown logic.

        在 FastAPI 启动過程中將策略與啟動函式作為背景任務執行，
        避免阻塞應用的啟動流程；於關閉時再取消這些任務。
        """
        # 在啟動階段建立背景任務
        background_tasks = [
            asyncio.create_task(strategy.run()) for strategy in self.strategies
        ]
        background_tasks.extend(
            asyncio.create_task(function()) for function in self.functions
        )

        try:
            # 立即進入應用生命週期（不阻塞）
            yield
        finally:
            # 應用關閉時取消所有背景任務
            for task in background_tasks:
                task.cancel()
            await asyncio.gather(*background_tasks, return_exceptions=True)
