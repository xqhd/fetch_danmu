from typing import List
import httpx
import re
import hashlib
import brotlicffi as brotli

from . import iqiyidm_pb2 as Iqiyidm_pb2

# import iqiyidm_pb2 as Iqiyidm_pb2
import asyncio
import time


def get_md5(str: str) -> str:
    md5 = hashlib.md5()
    md5.update(str.encode("utf-8"))
    return md5.hexdigest()


async def get_link(url, client: httpx.AsyncClient = None) -> List[str]:
    url_list = []
    headers = {
        "Accept-Encoding": "gzip,deflate,compress",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    }
    res = await client.get(url, headers=headers)
    js_url = re.findall(
        r'<script src="(.*?)" referrerpolicy="no-referrer-when-downgrade">',
        res.text,
    )
    if len(js_url) == 0:
        js_url = "//mesh.if.iqiyi.com/player/lw/lwplay/accelerator.js?apiVer=3"
    else:
        js_url = js_url[0]
    res = await client.get(f"https:{js_url}", headers={"referer": url})
    tv_id = re.findall('"tvId":([0-9]+)', res.text)[0]
    video_duration = int(re.findall('"videoDuration":([0-9]+)', res.text)[0])
    step_length = 60
    max_index = int(video_duration / step_length) + 1
    for index in range(1, max_index + 1):
        i = f"{tv_id}_{step_length}_{index}cbzuw1259a"
        s = get_md5(i)[-8:]
        o = f"{tv_id}_{step_length}_{index}_{s}.br"
        url_list.append(
            f"https://cmts.iqiyi.com/bullet/{tv_id[-4:-2]}/{tv_id[-2:]}/{o}"
        )
    return url_list


def parse_data(data):
    barrage_list = []
    for entry in data:
        for item in entry.bulletInfo:
            parsed_data = {}
            parsed_data.setdefault("text", item.content)
            parsed_data.setdefault("time", int(item.showTime))
            parsed_data.setdefault("color", "#FFFFFF")
            parsed_data.setdefault("style", {"size": 25})
            parsed_data["mode"] = 0
            parsed_data["border"] = False
            barrage_list.append(parsed_data)
    return barrage_list


def decompress_data(content):
    out = brotli.decompress(content)
    danmu = Iqiyidm_pb2.Danmu()
    danmu.ParseFromString(out)
    return danmu.entry


async def fetch_single_barrage(client: httpx.AsyncClient, url: str):
    try:
        res = await client.get(url)
        return parse_data(decompress_data(res.content))
    except Exception as e:
        print(f"获取弹幕失败 {url}: {e}")
        return []


async def read_barrage(urls: List[str], client: httpx.AsyncClient = None) -> List[dict]:
    barrage_list = []
    tasks = [fetch_single_barrage(client, url) for url in urls]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    for result in results:
        if isinstance(result, Exception):
            print(f"任务执行出错: {result}")
        else:
            barrage_list.extend(result)
    return barrage_list


async def get_iqiyi_danmu(url: str):
    danmu_list = []
    if "iqiyi.com" in url:
        async with httpx.AsyncClient() as client:
            urls = await get_link(url, client=client)
            danmu_list = await read_barrage(urls, client=client)
    return danmu_list


async def get_iqiyi_episode_url(url: str):
    from .utils import resolve_url_query
    from jsonpath_ng import parse

    if "iqiyi.com" in url:
        headers = {
            "Accept-Encoding": "gzip,deflate,compress",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        }
        async with httpx.AsyncClient(headers=headers) as client:
            try:
                query = resolve_url_query(url)
                if query.get("tvid"):
                    tv_id = query.get("tvid")[0]
                else:
                    res = await client.get(url)
                    js_url_matches = re.findall(
                        r'<script src="(.*?)" referrerpolicy="no-referrer-when-downgrade">',
                        res.text,
                    )
                    if not js_url_matches:
                        return {}
                    js_url = js_url_matches[0]
                    new_headers = headers.copy()
                    new_headers["referer"] = url
                    res = await client.get(f"https:{js_url}", headers=new_headers)
                    tv_id_matches = re.findall('"tvId":([0-9]+)', res.text)
                    if not tv_id_matches:
                        return {}
                    tv_id = tv_id_matches[0]
                params = f"entity_id={tv_id}&src=pca_tvg&timestamp={int(time.time())}&secret_key=howcuteitis"
                url = f"https://mesh.if.iqiyi.com/tvg/v2/lw/base_info?{params}&sign={get_md5(params).upper()}"
                another_headers = headers.copy()
                another_headers["referer"] = url
                res = await client.get(url, headers=another_headers)
                jsonpath_expr = parse("$..bk_title")
                matches = [match for match in jsonpath_expr.find(res.json())]
                result_objs = [
                    match.context.value for match in matches if match.value == "选集"
                ]
                url_dict = {}
                for result_obj in result_objs:
                    d = (
                        result_obj.get("data", {})
                        .get("data", [{}])[0]
                        .get("videos", {})
                    )
                    if isinstance(d, str):
                        _res = await client.get(d)
                        d = _res.json().get("data", {}).get("videos", {})
                    d = d.get("feature_paged", {})
                    for k in list(d.keys()):
                        for item in d[k]:
                            if item.get("page_url"):
                                url_dict[f"{item.get('album_order')}"] = item.get(
                                    "page_url"
                                )
                return url_dict
            except Exception:
                return {}
    return {}


if __name__ == "__main__":
    url = "https://www.iqiyi.com/v_26ecr2p42o0.html?vfm=m_331_dbdy&fv=4904d94982104144a1548dd9040df241&amp;subtype=9&amp;type=online-video&amp;link2key=52541a56ed"
    # asyncio.run(get_iqiyi_danmu(url))
    res = asyncio.run(get_iqiyi_danmu(url))
    print(res)
