import ipaddress
import socket
import netifaces
import os
import platform
import re


def get_192_subnet_hosts():
    all_hosts = []
    for interface in netifaces.interfaces():
        addrs = netifaces.ifaddresses(interface)
        if netifaces.AF_INET in addrs:
            for link in addrs[netifaces.AF_INET]:
                ip = link.get('addr')
                netmask = link.get('netmask')
                if ip and netmask and ip.startswith("192."):
                    try:
                        network = ipaddress.IPv4Network(f"{ip}/{netmask}", strict=False)
                        print(f"发现子网：{network}")
                        for host in network.hosts():
                            all_hosts.append(str(host))
                    except ValueError:
                        pass
    return all_hosts


def check_port_open(ip, port=24001, timeout=0.5):
    try:
        with socket.create_connection((ip, port), timeout=timeout):
            return True
    except (socket.timeout, socket.error):
        return False


def get_gateway_mac():
    """
    获取网段MAC
    :return:
    """
    gateways = netifaces.gateways()
    default_gateway = gateways.get('default', {}).get(netifaces.AF_INET)
    if default_gateway:
        gateway_ip = default_gateway[0]
        if platform.system() == 'Windows':
            output = os.popen(f"arp -a {gateway_ip}").read()
        else:
            output = os.popen(f"arp {gateway_ip}").read()

        # 使用正则提取 MAC 地址（支持 Windows 和 Linux/macOS 格式）
        mac_regex = r"(([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2}))"
        match = re.search(mac_regex, output)
        if match:
            return match.group(0)
    return None