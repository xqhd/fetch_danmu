import httpx
import asyncio
from typing import List
import re
import json


async def get_link(client, url) -> List:
    res = await client.get(url)
    vid_matches = re.findall('vid="(.*?)";', res.text)
    if not vid_matches:
        return []
    vid = vid_matches[0]
    aid_matches = re.findall('playlistId="(.*?)";', res.text)
    if not aid_matches:
        return []
    aid = aid_matches[0]
    base_url = f"https://api.danmu.tv.sohu.com/dmh5/dmListAll?act=dmlist_v2&request_from=h5_js&vid={vid}&aid={aid}&time_begin=%s&time_end=%s"
    return [base_url % (i * 300, (i + 1) * 300) for i in range(0, 20)]


def parse(data):
    data_list = []
    for d in data.get("info", {}).get("comments", []):
        parsed_data = {}
        parsed_data["time"] = d.get("v", 0)
        parsed_data["text"] = d.get("c", "")
        parsed_data["mode"] = 0
        parsed_data["color"] = "#FFFFFF"
        parsed_data["border"] = False
        parsed_data["style"] = {}
        data_list.append(parsed_data)
    return data_list


async def fetch_single_barrage(client, param):
    res = await client.get(param)
    return parse(res.json())


async def read_barrage(client, urls):
    tasks = [fetch_single_barrage(client, url) for url in urls]
    results = await asyncio.gather(*tasks)
    barrage_list = []
    for result in results:
        barrage_list.extend(result)
    return barrage_list


async def get_souhu_danmu(url: str):
    danmu_list = []
    if "tv.sohu.com" in url:
        async with httpx.AsyncClient() as client:
            urls = await get_link(client, url)
            danmu_list = await read_barrage(client, urls)
    return danmu_list


async def get_souhu_episode_url(url):
    if "tv.sohu.com" in url:
        async with httpx.AsyncClient() as client:
            _res = await client.get(url)
            vid_matches = re.findall('vid="(.*?)";', _res.text)
            if not vid_matches:
                return {}
            vid = vid_matches[0]
            play_list_id_matches = re.findall('playlistId="(.*?)";', _res.text)
            if not play_list_id_matches:
                return {}
            play_list_id = play_list_id_matches[0]
            params = {"playlistid": play_list_id, "vid": vid}
            res = await client.get("https://pl.hd.sohu.com/videolist", params)
            res.encoding = res.charset_encoding
            res_data = json.loads(res.text.encode("utf-8"))
            url_dict = {}
            for item in res_data.get("videos", []):
                url_dict[item.get("order")] = item.get("pageUrl")
            return url_dict
    return {}


if __name__ == "__main__":
    url = "https://tv.sohu.com/v/MjAyNDExMDcvbjYyMDAyMTM5Mi5zaHRtbA==.html"
    asyncio.run(get_souhu_danmu(url))
