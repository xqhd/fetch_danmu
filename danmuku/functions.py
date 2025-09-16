from .provides.bilibili.bilibili import get_bilibili_danmu, get_bilibili_episode_url
from .provides.iqiyi.iqiyi import get_iqiyi_danmu, get_iqiyi_episode_url
from .provides.mgtv import get_mgtv_danmu, get_mgtv_episode_url
from .provides.souhu import get_souhu_danmu, get_souhu_episode_url
from .provides.tencent import get_tencent_danmu, get_tencent_episode_url
from .provides.youku import get_youku_danmu, get_youku_episode_url
from .provides.utils import other2http
from .provides.doubai import (
    get_platform_link,
    douban_get_first_url,
    select_by_360,
    douban_select,
)
import asyncio
from .provides.caiji import get_vod_links_from_name
from typing import List, Dict, Optional, Any


def deduplicate_danmu(danmu_list: List[List[Any]]) -> List[List[Any]]:
    if not danmu_list:
        return danmu_list

    # 使用字典来存储每个text对应的最早弹幕
    seen_texts = {}
    deduplicated = []

    for danmu in danmu_list:
        text = danmu[4]  # text是第5个元素，索引为4
        time = danmu[0]  # time是第1个元素，索引为0

        if text not in seen_texts:
            seen_texts[text] = len(deduplicated)
            deduplicated.append(danmu)
        else:
            # 如果当前弹幕时间更早，替换已存储的弹幕
            existing_idx = seen_texts[text]
            if time < deduplicated[existing_idx][0]:
                deduplicated[existing_idx] = danmu

    # 按时间重新排序（因为可能有替换操作）
    deduplicated.sort(key=lambda x: x[0])

    return deduplicated


### url是官方视频播放链接
async def get_all_danmu(url: str) -> List[List[Any]]:
    all_danmu = []
    """使用异步并行执行所有平台获取弹幕"""
    if "mgtv.com" in url:
        results = await get_mgtv_danmu(url)
    elif "v.qq.com" in url:
        results = await get_tencent_danmu(url)
    elif "youku.com" in url:
        results = await get_youku_danmu(url)
    elif "iqiyi.com" in url:
        results = await get_iqiyi_danmu(url)
    elif "bilibili.com" in url:
        results = await get_bilibili_danmu(url)
    elif "tv.sohu.com" in url:
        results = await get_souhu_danmu(url)
    else:
        results = []
    if not results:
        return all_danmu

    all_danmu = [
        [
            item["time"],
            item["position"],
            item["color"],
            item["size"],
            item["text"],
        ]
        for item in results
    ]
    return all_danmu


### 这里使用官方链接中的第一个链接，在官方网页中获取该视频的所有链接
### 每个平台都有自己的方法，该方法主要用于根据视频名称查询
async def get_episode_url(platform_url_list: List[str]) -> Dict[str, List[str]]:
    """获取所有剧集链接"""
    url_dict = {}
    for platform_url in platform_url_list:
        tasks = [
            get_bilibili_episode_url(platform_url),
            get_iqiyi_episode_url(platform_url),
            get_souhu_episode_url(platform_url),
            get_tencent_episode_url(platform_url),
            get_youku_episode_url(platform_url),
            get_mgtv_episode_url(platform_url),
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        ## 过滤掉空字典并合并
        results = [
            result for result in results if result and not isinstance(result, Exception)
        ]
        if len(results) == 0:
            continue
        # 合并所有结果而不是只取第一个
        for result in results:
            for k, v in result.items():
                if k not in url_dict.keys():
                    url_dict[str(k)] = []
                url_dict[str(k)].append(v)
    return url_dict


async def get_platform_urls_by_id(douban_id: str) -> Dict[str, List[str]]:
    """获取豆瓣对应的平台链接"""
    platform_urls = await douban_get_first_url(douban_id)
    platform_url_list = other2http(platform_urls)
    url_dict = await get_episode_url(platform_url_list)
    if not url_dict:
        url_dict = await get_platform_link(douban_id)
    return url_dict


async def get_platform_urls_by_title(
    title: str, season_number: Optional[str], season: bool
) -> Dict[str, List[str]]:
    ### 首选查询 360 网站
    ### title 是视频名称
    ### season_number 是季数
    ### season 是是否是连续剧

    url_dict = {}
    _360data = await select_by_360(title, season_number, season)
    platform_url_list = []
    # 处理 _360data 为空的情况
    if _360data and _360data.get("playlinks"):
        for _, value in _360data.get("playlinks", {}).items():
            platform_url_list.append(value)

    url_dict = await get_episode_url(platform_url_list)

    ### 如果360网站没有查询到，则查询豆瓣
    if not url_dict:
        douban_data = await douban_select(title, season_number)
        # 处理 douban_data 为空的情况
        if douban_data and douban_data.get("target_id"):
            douban_id = douban_data["target_id"]
            url_dict = await get_platform_urls_by_id(douban_id)

    return url_dict


async def get_danmu_by_url(url: str) -> List[List[Any]]:
    danmu_data = await get_all_danmu(url)
    # 按时间排序
    danmu_data.sort(key=lambda x: x[0])
    # 去重复
    danmu_data = deduplicate_danmu(danmu_data)
    return danmu_data


async def get_danmu_by_id(id: str, episode_number: str) -> List[List[Any]]:
    all_danmu = []
    urls = await get_platform_urls_by_id(id)
    if not urls:
        return all_danmu
    if episode_number in urls:
        url = urls[episode_number]
    else:
        url = urls[list(urls.keys())[0]]
    for single_url in url:
        danmu_data = await get_all_danmu(single_url)
        all_danmu.extend(danmu_data)
    # 按时间排序
    all_danmu.sort(key=lambda x: x[0])
    # 去重复
    all_danmu = deduplicate_danmu(all_danmu)
    return all_danmu


async def get_danmu_by_title(
    title: str, season_number: Optional[str], season: bool, episode_number: str
) -> List[List[Any]]:
    all_danmu = []
    urls = await get_platform_urls_by_title(title, season_number, season)
    if not urls:
        return all_danmu
    if episode_number in urls:
        url = urls[episode_number]
    else:
        url = urls[list(urls.keys())[0]]
    for single_url in url:
        danmu_data = await get_all_danmu(single_url)
        all_danmu.extend(danmu_data)
    # 按时间排序
    all_danmu.sort(key=lambda x: x[0])
    # 去重复
    all_danmu = deduplicate_danmu(all_danmu)
    return all_danmu


async def get_danmu_by_title_caiji(title: str, episode_number: int) -> List[List[Any]]:
    all_danmu = []
    urls = await get_vod_links_from_name(title)
    if not urls:
        return all_danmu
    ## 如果有多个来源，只要第一个
    url_dict = {}
    for _, urls in urls.items():
        if urls:
            url_dict = urls
            break
    if not url_dict:
        return all_danmu

    if episode_number in url_dict:
        url = url_dict[episode_number]
    all_danmu = await get_all_danmu(url)
    # 去重复
    all_danmu = deduplicate_danmu(all_danmu)
    return all_danmu
