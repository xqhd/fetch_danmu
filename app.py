from robyn import Robyn, ALLOW_CORS
from robyn.openapi import (
    OpenAPI,
    OpenAPIInfo,
    Contact,
)
from robyn.robyn import QueryParams
from functions import (
    get_danmu_by_url,
    get_danmu_by_id,
    get_danmu_by_title,
    get_danmu_by_title_caiji,
)
from urllib.parse import unquote_plus


app = Robyn(
    __file__,
    openapi=OpenAPI(
        info=OpenAPIInfo(
            title="免费弹幕抓取",
            description="This is a free danmuku server.",
            version="1.0.0",
            contact=Contact(
                name="API Support",
                url="https://github.com/SeqCrafter/fetch_danmu",
                email="sdupan2015@gmail.com",
            ),
        ),
    ),
)

app.add_response_header("content-type", "application/json")

ALLOW_CORS(app, origins=["*"])


class UrlParams(QueryParams):
    url: str


class DoubanIdParams(QueryParams):
    douban_id: str
    episode_number: str


class TitleParams(QueryParams):
    title: str
    season_number: str
    season: bool
    episode_number: str


@app.get("/url")
async def danmu_by_url(query_params: UrlParams):
    """通过URL直接获取弹幕"""
    url = query_params.get("url", "")
    url = unquote_plus(url)
    if url:
        danmu_data = await get_danmu_by_url(url)
        return (
            {
                "code": 0,
                "name": url,
                "danmu": len(danmu_data),
                "danmuku": danmu_data,
            },
            {},
            200,
        )
    else:
        return {"error": "url is required"}, {}, 400


@app.get("/douban_id")
async def danmu_by_douban_id(query_params: DoubanIdParams):
    """通过豆瓣ID直接获取弹幕"""
    douban_id = query_params.get("douban_id", "")
    episode_number = query_params.get("episode_number", "")
    all_danmu = []
    if not douban_id or not episode_number:
        return {"error": "douban_id and episode_number are required"}, {}, 400
    all_danmu = await get_danmu_by_id(douban_id, episode_number)
    return (
        {
            "code": 0,
            "name": douban_id,
            "danmu": len(all_danmu),
            "danmuku": all_danmu,
        },
        {},
        200,
    )


@app.get("/title")
async def danmu_by_title(query_params: TitleParams):
    """通过视频名称直接获取弹幕"""
    title = unquote_plus(query_params.get("title", ""), encoding="utf-8")
    season_number = query_params.get("season_number", "")
    season = query_params.get("season", "")
    episode_number = query_params.get("episode_number", "")
    if season == "False" or season == "false" or season == "0":
        season = False
    else:
        season = True
    if not title or not season_number or not episode_number or type(season) is not bool:
        return (
            {"error": "title, season_number, episode_number and season are required"},
            {},
            400,
        )
    all_danmu = await get_danmu_by_title(title, season_number, season, episode_number)
    return (
        {
            "code": 0,
            "name": title,
            "danmu": len(all_danmu),
            "danmuku": all_danmu,
        },
        {},
        200,
    )


@app.get("/test/title")
async def danmu_by_title_caiji(query_params: TitleParams):
    """通过视频名称直接获取弹幕"""
    title = unquote_plus(query_params.get("title", ""), encoding="utf-8")
    season_number = query_params.get("season_number", "1")
    season = query_params.get("season", "")
    episode_number = query_params.get("episode_number", "")
    if season == "False" or season == "false" or season == "0":
        season = False
    else:
        season = True
    if not title or not season_number or not episode_number or type(season) is not bool:
        return (
            {"error": "title, season_number, episode_number and season are required"},
            {},
            400,
        )
    if season:
        all_danmu = await get_danmu_by_title_caiji(title, int(episode_number))
    else:
        all_danmu = await get_danmu_by_title_caiji(title, 1)
    return (
        {
            "code": 0,
            "name": title,
            "danmu": len(all_danmu),
            "danmuku": all_danmu,
        },
        {},
        200,
    )


if __name__ == "__main__":
    app.start(host="0.0.0.0", port=8080)
