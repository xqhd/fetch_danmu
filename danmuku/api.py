from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Annotated, List, Any
from urllib.parse import unquote_plus
import httpx
import io
from .functions import (
    get_danmu_by_url,
    get_danmu_by_id,
    get_danmu_by_title,
    get_danmu_by_title_caiji,
)


class DanmukuResponse(BaseModel):
    code: int
    name: str
    danmu: int
    danmuku: List[List[Any]]


# 创建 FastAPI 应用实例
fastapi_app = FastAPI(
    title="免费弹幕抓取",
    description="This is a free danmuku server.",
    version="1.0.0",
    contact={
        "name": "API Support",
        "url": "https://github.com/SeqCrafter/fetch_danmu",
        "email": "sdupan2015@gmail.com",
    },
)

# 添加 CORS 中间件
fastapi_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@fastapi_app.get("/api/url", response_model=DanmukuResponse)
async def danmu_by_url(
    url: Annotated[str, Query(description="视频URL地址", pattern=r"^https?://.*$")],
):
    """通过URL直接获取弹幕"""
    # URL解码
    decoded_url = unquote_plus(url)
    danmu_data = await get_danmu_by_url(decoded_url)
    return {
        "code": 0,
        "name": decoded_url,
        "danmu": len(danmu_data),
        "danmuku": danmu_data,
    }


@fastapi_app.get("/api/douban_id", response_model=DanmukuResponse)
async def danmu_by_douban_id(
    douban_id: Annotated[int, Query(description="豆瓣ID")],
    episode_number: Annotated[int, Query(description="集数")],
):
    all_danmu = await get_danmu_by_id(str(douban_id), str(episode_number))
    return {
        "code": 0,
        "name": str(douban_id),
        "danmu": len(all_danmu),
        "danmuku": all_danmu,
    }


@fastapi_app.get("/api/title", response_model=DanmukuResponse)
async def danmu_by_title(
    title: Annotated[str, Query(description="视频名称")],
    season_number: Annotated[int, Query(description="季数")],
    season: Annotated[bool, Query(description="是否为连续剧, true/false")],
    episode_number: Annotated[int, Query(description="集数")],
):
    """通过视频名称直接获取弹幕"""

    all_danmu = await get_danmu_by_title(
        title, str(season_number), season, str(episode_number)
    )
    return {
        "code": 0,
        "name": title,
        "danmu": len(all_danmu),
        "danmuku": all_danmu,
    }


@fastapi_app.get("/api/test/title", response_model=DanmukuResponse)
async def danmu_by_title_caiji(
    title: Annotated[str, Query(description="视频名称")],
    season: Annotated[bool, Query(description="是否为连续剧, true/false")],
    episode_number: Annotated[int, Query(description="集数")],
    season_number: Annotated[str | None, Query(description="季数")] = None,
):
    """通过视频名称直接获取弹幕（测试版本）"""

    if season:
        all_danmu = await get_danmu_by_title_caiji(title, episode_number)
    else:
        all_danmu = await get_danmu_by_title_caiji(title, 1)
    ## to avoid type error
    print(season_number)

    return {
        "code": 0,
        "name": title,
        "danmu": len(all_danmu),
        "danmuku": all_danmu,
    }


@fastapi_app.get("/api/proxy/image")
async def proxy_image(url: Annotated[str, Query(description="图片URL地址")]):
    """代理图片请求，解决跨域和防盗链问题"""
    try:
        # 解码URL
        decoded_url = unquote_plus(url)

        # 设置适当的请求头来模拟浏览器访问
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Referer": "https://movie.douban.com/",
            "Accept": "image/webp,image/apng,image/*,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(decoded_url, headers=headers, timeout=30.0)
            response.raise_for_status()

            # 获取内容类型
            content_type = response.headers.get("content-type", "image/jpeg")

            # 创建流式响应
            def generate():
                yield response.content

            return StreamingResponse(
                io.BytesIO(response.content),
                media_type=content_type,
                headers={
                    "Cache-Control": "public, max-age=86400",  # 缓存1天
                    "Access-Control-Allow-Origin": "*",
                },
            )

    except httpx.RequestError as e:
        raise HTTPException(status_code=500, detail=f"请求图片失败: {str(e)}")
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"图片服务器返回错误: {e.response.status_code}",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"代理图片时发生错误: {str(e)}")
