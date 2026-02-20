import os
from datetime import datetime
from pathlib import Path

import yaml
from datetime import datetime, timedelta, timezone


def get_iso_now():
    """
    获取当前时间的 ISO 8601 格式
    :return:
    """

    iso_now = datetime.now().astimezone().replace(microsecond=0).isoformat()

    return iso_now


def generate_bid():
    """
    生成BID
    :return:
    """
    bid = os.urandom(16)

    return bid.hex()


def generate_bid_v2(node_bid):
    """
    生成BID 需要节点BID
    :return:
    """
    bid = node_bid[:10] + os.urandom(11).hex()

    return bid


def extract_by_space(text, position):
    """
    数据由空格分开 position 获取第几条数据
    :param text: 输入
    :param position: 位置
    :return:
    """
    # Remove any trailing spaces first
    input_str = text.rstrip()

    # Initialize variables
    last_index = 0
    space_count = 0

    # Loop through the string to find space positions
    while space_count < position - 1:
        space_index = input_str.find(' ', last_index)
        if space_index == -1:
            return None  # Not enough spaces found
        last_index = space_index + 1
        space_count += 1

    # Find the start of the next part
    space_index = input_str.find(' ', last_index)
    if space_index == -1:
        return input_str[last_index:]  # If no more spaces, return the rest of the string
    else:
        return input_str[last_index:space_index]  # Return the part between the spaces


def save_dict_to_yaml(data, file_path):
    # 创建上级目录（如果不存在）
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    with open(file_path, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, allow_unicode=True, sort_keys=False)

def yaml_data(file_path, mode="r"):
    """
    加载本地yaml为字典
    :param file_path:
    :param mode:
    :return:
    """
    with open(file_path, mode, encoding="utf-8") as file:
        data = yaml.safe_load(file)

    if data is None:
        return {}
    return data

def get_yaml_files(directory):
    """
    获取目录下的所有 YAML 文件，并加载为字典
    :param directory: 目录路径
    :return: [{'file': file_path, 'data': dict}, ...]
    """
    dir_path = Path(directory)
    yaml_files = list(dir_path.glob("*.yml")) + list(dir_path.glob("*.yaml"))
    results = []

    for file in yaml_files:
        try:
            data = yaml_data(file)
            results.append({'file': str(file), 'data': data})
        except Exception as e:
            print(f"Error loading {file}: {e}")

    return results

def save_to_yaml(data: dict, file_path: str, mode: str = "w") -> None:
    """
    将字典保存为本地yaml文件

    :param data: 要保存的字典数据
    :param file_path: 保存的文件路径
    :param mode: 文件写入模式，默认为 'w'（覆盖写入）
    """
    with open(file_path, mode, encoding="utf-8") as file:
        yaml.safe_dump(data, file, allow_unicode=True)

def file_split_chunk(file_path, output_dir, chunk_size=1 * 1024 * 1024):
    """
    将文件按指定字节数进行分块
    :param file_path: 待分割的文件路径
    :param chunk_size: 每个块的大小（单位：字节）
    :param output_dir: 分块路径
    :return: (chunk_paths, total_chunks) 分块路径列表和总块数
    """
    os.makedirs(output_dir, exist_ok=True)

    chunk_paths = []
    file_size = os.path.getsize(file_path)
    total_chunks = (file_size + chunk_size - 1) // chunk_size

    with open(file_path, 'rb') as f:
        for i in range(total_chunks):
            chunk_data = f.read(chunk_size)
            chunk_path = os.path.join(output_dir, f"chunk_{i:04d}.part")
            with open(chunk_path, 'wb') as chunk_file:
                chunk_file.write(chunk_data)
            chunk_paths.append(chunk_path)

    return chunk_paths

def get_datetime_after_days(days: int) -> str:
    """
    获取从当前 UTC 时间起，经过指定天数后的 ISO 8601 格式时间字符串。

    :param days: 要添加的天数
    :return: 返回 ISO 8601 格式的时间字符串
    """
    # 获取当前 UTC 时间
    current_datetime = datetime.now(timezone.utc)

    # 计算指定天数后的时间
    new_datetime = current_datetime + timedelta(days=days)

    # 将 datetime 转换为 ISO 8601 格式的字符串
    formatted_datetime = new_datetime.astimezone(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')

    return formatted_datetime