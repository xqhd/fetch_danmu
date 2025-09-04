from curl_cffi import requests

API_URL = "https://www.caiji.cyou/api.php/provide/vod/"


async def get_id(vod_name: str, client: requests.AsyncSession):
    params = {
        "ac": "list",
        "wd": vod_name,
    }
    res = await client.get(API_URL, params=params, impersonate="chrome124")
    if res.status_code != 200:
        return None
    data = res.json()
    ## 只返回第一个最佳匹配，没想到更好的方法
    return data["list"][0]["vod_id"]


def correct_episode_str(episode_str: str) -> int:
    if not episode_str:
        return -1

    try:
        episode_numbers = re.findall(r"\d+", episode_str)
        if episode_numbers:
            episode_num = int(episode_numbers[0])
            return episode_num
        else:
            return -1
    except (ValueError, TypeError) as e:
        return -1


async def get_vod_urls(vod_id: int, client: requests.AsyncSession):
    params = {
        "ac": "detail",
        "ids": vod_id,
    }
    vod_links = {}
    res = await client.get(API_URL, params=params, impersonate="chrome124")
    if res.status_code != 200 or not res.json()["list"]:
        return None
    urls = res.json()["list"][0]["vod_play_url"].split("$$$")
    sources = res.json()["list"][0]["vod_play_from"].split("$$$")

    for source_name, source_url in zip(sources, urls):
        single_source_links = {}
        if not source_url:
            continue
        episode_links = source_url.split("#")
        vod_type = "tv" if len(episode_links) > 1 else "movie"
        for episode_link in episode_links:
            if not episode_link or "$" not in episode_link:
                continue
            episode_str, link = episode_link.split("$", 1)  # 只分割第一个$
            episode_index = correct_episode_str(episode_str)
            if episode_index != -1 and link.strip():
                single_source_links[episode_index] = link.strip()
            else:
                if vod_type == "movie":
                    single_source_links[1] = link.strip()
        if single_source_links:
            vod_links[source_name] = single_source_links
    return vod_links


async def get_vod_links_from_name(vod_name: str):
    vod_links = {}
    async with requests.AsyncSession() as client:
        vod_id = await get_id(vod_name, client)
        if not vod_id:
            return None
        vod_links = await get_vod_urls(vod_id, client)
        if vod_links:
            return vod_links
    return vod_links
