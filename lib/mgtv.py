import asyncio
from typing import List
import httpx


def time_to_second(time: list):
    s = 0
    m = 1
    for d in time[::-1]:
        s += m * int(d)
        m *= 60
    return s


async def get_link(client, url) -> List[str]:
    api_video_info = "https://pcweb.api.mgtv.com/video/info"
    api_danmaku = "https://galaxy.bz.mgtv.com/rdbarrage"
    _u = url.split(".")[-2].split("/")
    if len(_u) < 2:
        return []
    cid = _u[-2]
    vid = _u[-1]
    params = {
        "cid": cid,
        "vid": vid,
    }
    res = await client.get(url=api_video_info, params=params)
    _time = res.json().get("data", {}).get("info", {}).get("time")
    if not _time or ":" not in _time:
        return []
    end_time = time_to_second(_time.split(":")) * 1000

    return [
        f"{api_danmaku}?vid={vid}&cid={cid}&time={item}"
        for item in range(0, end_time, 60 * 1000)
    ]


def parse_data(data):
    barrage_list = []
    if data.get("data", {}).get("items", []) is None:
        return []
    for item in data.get("data", {}).get("items", []):
        parsed_data = {}
        parsed_data["text"] = item.get("content", "")
        parsed_data["time"] = item.get("time", 0) / 1000
        parsed_data["mode"] = 0
        parsed_data["color"] = "#FFFFFF"
        parsed_data["border"] = False
        parsed_data["style"] = {}
        barrage_list.append(parsed_data)
    return barrage_list


async def fetch_single_barrage(client, param):
    res = await client.get(param)
    return parse_data(res.json())


async def read_barrage(client, params):
    tasks = [fetch_single_barrage(client, param) for param in params]
    results = await asyncio.gather(*tasks)
    barrage_list = []
    for res in results:
        if res:
            barrage_list.extend(res)
    return barrage_list


async def get_mgtv_danmu(url: str):
    danmu_list = []
    if "mgtv.com" in url:
        async with httpx.AsyncClient() as client:
            urls = await get_link(client, url)
            danmu_list = await read_barrage(client, urls)
    return danmu_list


if __name__ == "__main__":
    url = (
        "https://www.mgtv.com/b/755976/23118095.html?fpa=1261&fpos=&lastp=ch_tv&cpid=4"
    )
    asyncio.run(get_mgtv_danmu(url))
