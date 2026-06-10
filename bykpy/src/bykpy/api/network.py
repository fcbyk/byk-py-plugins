"""网络工具函数。"""
import socket
from typing import List, Dict


# 网络接口分类规则：(关键词列表，类型名称，是否虚拟接口，优先级)
IFACE_RULES = [
    (['vmware', 'vmnet'],         'vmware',     True,  30),
    (['vbox', 'virtualbox'],      'virtualbox', True,  30),
    (['docker', 'wsl'],           'container',  True,  40),
    (['bluetooth'],               'bluetooth',  True,  60),
    (['ethernet', '以太网'],       'ethernet',   False, 10),
    (['wlan', 'wi-fi', '无线'],   'wifi',       False, 10),
    (['loopback'],                'loopback',   True,  100),
]


def detect_iface_type(iface: str) -> tuple[str, bool, int]:
    """检测网络接口类型。"""
    lname = iface.lower()
    for keywords, t, virtual, prio in IFACE_RULES:
        if any(k in lname for k in keywords):
            return t, virtual, prio
    return 'unknown', False, 50


def get_private_networks() -> List[Dict]:
    """获取所有局域网 IP 地址信息。

    依赖 psutil，缺失时抛出 ImportError（含安装指引）。
    """
    try:
        import psutil
    except ImportError:
        raise ImportError(
            "psutil is required for get_private_networks.\n"
            "Install it and add to your plugin dependencies:\n"
            "    pip install psutil\n"
            "    # then add 'psutil>=5.9.0' to pyproject.toml dependencies"
        )

    results = []
    interfaces = psutil.net_if_addrs()

    for iface, addrs in interfaces.items():
        ips = []
        iface_type, is_virtual, priority = detect_iface_type(iface)

        for addr in addrs:
            if addr.family != socket.AF_INET:
                continue

            ip = addr.address

            # 跳过回环地址和链路本地地址
            if ip.startswith('127.'):
                continue
            if ip.startswith('169.254.'):
                continue
            # 只保留私有 IP 地址
            if ip.startswith(('10.', '192.168.', '172.')):
                ips.append(ip)

        if ips:
            results.append({
                "iface": iface,
                "ips": ips,
                "type": iface_type,
                "virtual": is_virtual,
                "priority": priority
            })

    # 按优先级排序（数字越小优先级越高）
    results.sort(key=lambda x: x['priority'])
    
    # 如果没有找到任何局域网 IP，返回 localhost
    if not results:
        results.append({
            "iface": "localhost",
            "ips": ["127.0.0.1"],
            "type": "loopback",
            "virtual": True,
            "priority": 100
        })
    
    return results


def ensure_port_available(port: int, host: str = "0.0.0.0") -> None:
    """检查端口是否可用。"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((host, int(port)))
