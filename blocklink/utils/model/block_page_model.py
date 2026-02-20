from dataclasses import dataclass
from typing import Any, List

from blocklink.utils.block_model import BlockModel


@dataclass
class BlockPageModel:
    """分页数据模型

    用于封装分页查询的结果数据

    Attributes:
        page: 当前页码
        count: 总记录数
        data: 分页元数据
        limit: 每页记录数限制
        items: 当前页的 BlockModel 列表
    """
    page: int
    count: int
    data: dict[str, Any]
    limit: int
    items: List[BlockModel]

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'BlockPageModel':
        """从字典创建 BlockPageModel 实例

        Args:
            data: 包含分页数据的字典，格式如下：
                {
                    "page": int,
                    "count": int,
                    "data": dict,
                    "limit": int,
                    "items": list[dict]  # 每个 dict 将被转换为 BlockModel
                }

        Returns:
            BlockPageModel 实例

        Example:
            >>> page_data = {
            ...     "page": 1,
            ...     "count": 100,
            ...     "data": {"some": "metadata"},
            ...     "limit": 10,
            ...     "items": [{"bid": "123", "name": "test"}, ...]
            ... }
            >>> page_model = BlockPageModel.from_dict(page_data)
        """
        # 处理 items，将每个字典转换为 BlockModel
        block_models = []
        for item in data.get("items", []):
            if isinstance(item, dict):
                block_model = BlockModel(data=item)
                block_models.append(block_model)
            elif isinstance(item, BlockModel):
                block_models.append(item)
            else:
                # 如果 item 既不是 dict 也不是 BlockModel，跳过
                continue

        return cls(
            page=data.get("page", 1),
            count=data.get("count", 0),
            data=data.get("data", {}),
            limit=data.get("limit", 10),
            items=block_models
        )

    @property
    def total_pages(self) -> int:
        """计算总页数"""
        return (self.count + self.limit - 1) // self.limit

    @property
    def has_next(self) -> bool:
        """是否有下一页"""
        return self.page < self.total_pages

    @property
    def has_previous(self) -> bool:
        """是否有上一页"""
        return self.page > 1

    @property
    def items_count(self) -> int:
        """当前页项目数量"""
        return len(self.items)

    def get_block_by_bid(self, bid: str) -> BlockModel | None:
        """根据 BID 获取 BlockModel

        Args:
            bid: 块的唯一标识符

        Returns:
            匹配的 BlockModel 或 None
        """
        for block in self.items:
            if block.bid == bid:
                return block
        return None

