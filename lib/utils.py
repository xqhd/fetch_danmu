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
