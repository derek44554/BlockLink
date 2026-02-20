"""
blocklink - A distributed node network framework
"""

__version__ = '0.1.0'
__author__ = 'Derek X'
__email__ = 'me@derekx.com'

# 导出主要组件（根据需要调整）
from blocklink.models.node.node_manager import NODE_MANAGER
from blocklink.models.connect.connect_manager import CONNECT_MANAGER
from blocklink.strategy.strategy_manager import StrategyManager

__all__ = [
    '__version__',
    'NODE_MANAGER',
    'CONNECT_MANAGER',
    'StrategyManager',
]
