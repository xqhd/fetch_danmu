from fastapi import FastAPI, HTTPException, status, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import asyncio
from .lib.doubai_search import get_platform_link, douban_select, douban_get_first_url
from .lib.bilibili import get_bilibili_danmu, get_bilibili_episode_url
from .lib.iqiyi import get_iqiyi_danmu, get_iqiyi_episode_url
from .lib.mgtv import get_mgtv_danmu
from .lib.souhu import get_souhu_danmu, get_souhu_episode_url
from .lib.tencent import get_tencent_danmu, get_tencent_episode_url
from .lib.youku import get_youku_danmu, get_youku_episode_url
from .lib.utils import other2http


# Pydantic Models
class DanmuItem(BaseModel):
    """弹幕项目模型"""

    text: str = Field(..., description="弹幕内容")
    time: float = Field(..., ge=0, description="弹幕时间(秒)")
    color: str = Field(default="#FFFFFF", description="弹幕颜色")
    mode: int = Field(default=0, ge=0, le=2, description="弹幕模式")
    style: Dict[str, Any] = Field(default_factory={}, description="弹幕样式")
    border: bool = Field(default=False, description="是否有边框")


class ApiResponse(BaseModel):
    """统一API响应模型"""

    code: int = Field(..., description="响应码, 0表示成功, -1表示失败")
    msg: Optional[str] = Field(None, description="错误信息")
    data: Optional[List[DanmuItem]] = Field(None, description="弹幕数据")


class ErrorResponse(BaseModel):
    """错误响应模型"""

    code: int = Field(-1, description="错误码")
    msg: str = Field(..., description="错误信息")


app = FastAPI(
    title="弹幕获取API",
    description="异步获取各大视频平台弹幕的FastAPI服务",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)


class DanmuService:
    """弹幕服务类"""

    @staticmethod
    async def get_all_danmu(url: str) -> List[DanmuItem]:
        """使用异步并行执行所有平台获取弹幕"""
        tasks = [
            get_tencent_danmu(url),
            get_youku_danmu(url),
            get_iqiyi_danmu(url),
            get_bilibili_danmu(url),
            get_mgtv_danmu(url),
            get_souhu_danmu(url),
        ]

        try:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            # print(results)
            # 合并所有非空结果和非异常结果
            all_danmu = []
            for result in results:
                if isinstance(result, Exception):
                    continue  # 忽略异常结果
                if result:
                    all_danmu.extend([DanmuItem(**item) for item in result])
            return all_danmu
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"获取弹幕时发生错误: {str(e)}",
            )

    @staticmethod
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
            ]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            ## 过滤掉空字典并合并
            results = [result for result in results if result and not isinstance(result, Exception)]
            if len(results) == 0:
                continue
            # 合并所有结果而不是只取第一个
            for result in results:
                for k, v in result.items():
                    if k not in url_dict.keys():
                        url_dict[str(k)] = []
                    url_dict[str(k)].append(v)
        return url_dict

    @staticmethod
    async def get_platform_urls(douban_id: str) -> Dict[str, List[str]]:
        """获取豆瓣对应的平台链接"""
        platform_urls = await douban_get_first_url(douban_id)
        platform_url_list = other2http(platform_urls)
        url_dict = await DanmuService.get_episode_url(platform_url_list)
        if not url_dict:
            url_dict = await get_platform_link(douban_id)
        return url_dict


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    """HTTP异常处理器"""
    return JSONResponse(
        status_code=exc.status_code, content=ErrorResponse(msg=exc.detail).model_dump()
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc: Exception):
    """通用异常处理器"""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(msg=f"服务器内部错误: {str(exc)}").model_dump(),
    )


@app.get(
    "/danmu/by_douban_id",
    response_model=ApiResponse,
    status_code=status.HTTP_200_OK,
    summary="通过豆瓣ID获取弹幕",
    description="根据豆瓣ID获取对应视频的弹幕数据",
    responses={
        200: {"model": ApiResponse, "description": "成功获取弹幕"},
        404: {"model": ErrorResponse, "description": "未找到对应的视频链接"},
        500: {"model": ErrorResponse, "description": "服务器内部错误"},
    },
)
async def danmu_by_douban_id(
    douban_id: str = Query(..., description="豆瓣ID"),
    episode_number: Optional[int] = Query(None, ge=1, description="集数, 可选"),
):
    """通过豆瓣ID获取弹幕"""
    platform_urls = await DanmuService.get_platform_urls(douban_id)
    if not platform_urls:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="未找到对应的视频链接"
        )
    # print(platform_urls)
    # 如果指定了集数, 只获取该集的弹幕
    if episode_number is not None and str(episode_number) in platform_urls:
        urls = platform_urls[str(episode_number)]
    else:
        # 获取第一集或所有集的链接
        first_key = list(platform_urls.keys())[0]
        urls = platform_urls[first_key]
    # print(urls)
    # 并行获取所有链接的弹幕
    all_danmu = []
    for url in urls:
        danmu_data = await DanmuService.get_all_danmu(url)
        all_danmu.extend(danmu_data)

    # 按时间排序
    all_danmu.sort(key=lambda x: x.time)

    return ApiResponse(code=0, data=all_danmu)


@app.get(
    "/danmu/by_title",
    response_model=ApiResponse,
    status_code=status.HTTP_200_OK,
    summary="通过标题获取弹幕",
    description="根据视频标题搜索并获取弹幕数据",
    responses={
        200: {"model": ApiResponse, "description": "成功获取弹幕"},
        404: {"model": ErrorResponse, "description": "未找到对应的豆瓣信息"},
        500: {"model": ErrorResponse, "description": "服务器内部错误"},
    },
)
async def danmu_by_title(
    title: str = Query(..., min_length=1, description="视频标题"),
    season_number: Optional[int] = Query(1, ge=1, description="季数, 默认为1"),
    episode_number: Optional[int] = Query(None, ge=1, description="集数, 可选"),
):
    """通过标题获取弹幕"""
    # 通过标题搜索豆瓣ID
    douban_data = await douban_select(title, season_number)
    if not douban_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="未找到对应的豆瓣信息"
        )

    douban_id = douban_data["target_id"]
    # print(douban_id)
    # 调用豆瓣ID接口
    return await danmu_by_douban_id(douban_id, episode_number)


@app.get(
    "/danmu/by_url",
    response_model=ApiResponse,
    status_code=status.HTTP_200_OK,
    summary="通过URL直接获取弹幕",
    description="直接从视频URL获取弹幕数据",
    responses={
        200: {"model": ApiResponse, "description": "成功获取弹幕"},
        500: {"model": ErrorResponse, "description": "服务器内部错误"},
    },
)
async def danmu_by_url(url: str = Query(..., min_length=1, description="视频URL")):
    """通过URL直接获取弹幕"""
    # 直接获取URL对应的弹幕
    danmu_data = await DanmuService.get_all_danmu(url)

    # 按时间排序
    danmu_data.sort(key=lambda x: x.time)

    return ApiResponse(code=0, data=danmu_data)


@app.get("/health")
async def health_check():
    """健康检查接口"""
    return {"status": "healthy", "service": "danmu-api"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True,  # 开发环境启用热重载
        log_level="info",
    )
