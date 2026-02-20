from blocklink.utils.api import bridge_request
from blocklink.utils.model.block_page_model import BlockPageModel


def tag_count(name, receiver="") -> int:
    data = {"name": name}
    request = bridge_request(protocol="cert", routing="/block/tag/count", data=data, receiver=receiver)

    count = request.json()["data"]["count"]
    return count

def tag_multiple(name, page, receiver="") -> BlockPageModel:
    """获取指定标签的分页数据
    
    Args:
        name: 标签名称
        page: 页码
        receiver: 接收者
        
    Returns:
        BlockPageModel 对象，包含分页信息和 BlockModel 列表
    """
    data = {"name": name, "page": page}
    request = bridge_request(protocol="cert", routing="/block/tag/multiple", data=data, receiver=receiver)
    
    response_data = request.json()["data"]
    
    # 使用 from_dict 方法创建 BlockPageModel
    return BlockPageModel.from_dict(response_data)

