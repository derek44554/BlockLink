"""
blocklink - A distributed node network framework
"""

__version__ = '0.1.2'
__author__ = 'Derek X'
__email__ = 'me@derekx.com'

import os
from dotenv import load_dotenv

# 加载 .env 文件（如果存在）
load_dotenv()

# 设置默认环境变量（如果不存在）
# setdefault 只在环境变量不存在时才设置，不会覆盖已有的值
os.environ.setdefault('SIGNATURE_PATH', 'resources/signature.yml')
os.environ.setdefault('TOP_VERIFY_PUBLIC_PEY_PATH', 'resources/public_key_top.pem')
os.environ.setdefault('NODE_PRIVATE_PEY_PATH', 'resources/private_key.pem')
os.environ.setdefault('NODE_PUBLIC_PEY_PATH', 'resources/public_key.pem')

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
