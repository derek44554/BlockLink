import requests


def bridge_request(protocol, routing, data: dict, receiver="", wait=True, timeout=60):
    data = {
        "protocol": protocol,
        "routing": routing,
        "data": data,
        "receiver": receiver,
        "wait": wait,
        "timeout": timeout,
    }
    response = requests.post(url="http://127.0.0.1:24005/bridge/ins", json=data)

    return response
