import re
from typing import List
from urllib.parse import urlparse
from urllib import parse


def resolve_url_query(url: str) -> dict[str, list[str]]:
    _url = urlparse(url)
    parad = parse.parse_qs(_url.query)
    return parad


def other2http(platform_url_list: List[str]):
    ret_list = []
    for url in platform_url_list:
        if not url.startswith("http"):
            agreement = re.findall("^(.*?):", url)
            query = resolve_url_query(url)
            match agreement:
                case ["txvideo"]:
                    url = f"https://v.qq.com/x/cover/{query.get('cid')[0]}/{query.get('vid')[0]}.html"
                case ["iqiyi"]:
                    url = f"http://www.iqiyi.com?tvid={query.get('tvid')[0]}"
        ret_list.append(url)
    return ret_list


def int_to_hex_color(decimal: int) -> str:
    # 将十进制数转换为 6 位十六进制字符串，去掉 '0x' 前缀，补齐 6 位
    hex_str = f"{decimal:06X}"
    # 确保输出长度为 6（若输入过大，截取最后 6 位）
    hex_str = hex_str[-6:] if len(hex_str) > 6 else hex_str.zfill(6)
    # 添加 # 前缀并返回
    return f"#{hex_str}"
