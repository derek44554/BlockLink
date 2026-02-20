"""
blocklink - A distributed node network framework
"""

__version__ = '0.1.0'
__author__ = 'Derek X'
__email__ = 'me@derekx.com'

from dotenv import load_dotenv
try:
    load_dotenv()
except:
    print(".env is required and needs to be configured.")

# 导出主要组件（根据需要调整）
from blocklink.models.node.node_manager import NodeManager
from blocklink.models.connect.connect_manager import ConnectManager
from blocklink.strategy.strategy_manager import StrategyManager



__all__ = [
    '__version__',
    'NodeManager',
    'ConnectManager',
    'StrategyManager',
]
