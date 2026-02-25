from setuptools import setup, find_packages
import os

# 从 __init__.py 读取版本号
def get_version():
    init_path = os.path.join(os.path.dirname(__file__), 'blocklink', '__init__.py')
    with open(init_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith('__version__'):
                return line.split('=')[1].strip().strip("'\"")
    raise RuntimeError('Unable to find version string.')

setup(
    name='blocklink',  # PyPI 上的包名
    version=get_version(),
    packages=find_packages(exclude=['tests', 'tests.*']),
    install_requires=[
        'cryptography>=41.0.0',
        'pyyaml>=6.0',
        'starlette>=0.27.0',
        'websockets>=11.0',
        'uvicorn>=0.23.0',
        'sqlmodel>=0.0.8',
        'python-dotenv>=1.0.0',
        'fastapi>=0.100.0',
        'requests>=2.31.0',
        'netifaces>=0.11.0',
        'pycryptodome>=3.18.0',
        'Pillow>=10.0.0',
    ],
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    author='Derek X',  # 请修改为你的真实姓名
    author_email='me@derekx.com',  # 请修改为你的邮箱
    description='A distributed node network framework for secure registration and instruction transmission',
    license='MIT',
    url='https://github.com/derek44554/BlockLink',  # 请修改为你的 GitHub 仓库地址
    project_urls={
        'Bug Reports': 'https://github.com/derek44554/BlockLink/issues',
        'Source': 'https://github.com/derek44554/BlockLink',
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Networking',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.10',
    keywords='distributed, networking, protocol, blockchain, node',
)