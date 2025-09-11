import reflex as rx
from ..template import template
from urllib.parse import unquote_plus
from ..functions import get_danmu_by_url
import json
import re


class PreviewState(rx.State):
    json_data: str = ""
    loading: bool = True
    show_code: bool = False
    code: str = ""
    rq_url: str = ""

    @rx.event
    def get_code(self) -> None:
        current_host = self.router.url.origin
        schema = self.router.url.scheme
        if schema == "https":
            ## using domain
            current_host = self.router.url.domain
        else:
            backend_host = re.sub(r":\d+", ":8080", current_host)
            current_host = backend_host
        self.code = f"curl {current_host}/api/url?url={self.rq_url}"
        self.show_code = True

    @rx.event
    async def load_json_data(self) -> None:
        ## reset all state
        self.reset()
        yield
        args = self.router.url.query_parameters
        url = args.get("url", "")
        url = unquote_plus(url)
        self.rq_url = url
        json_data = await get_danmu_by_url(url)
        ## only show the first 100 danmu
        json_dict = {
            "code": 0,
            "name": url,
            "danmu": len(json_data),
            "danmuku": json_data[:100],
        }
        pretty_json = json.dumps(json_dict, indent=4, ensure_ascii=False)
        self.json_data = pretty_json
        self.loading = False
        yield


def code_block(code: str, language: str):
    return rx.box(
        rx._x.code_block(
            code,
            language=language,
            class_name="code-block max-h-[450px] overflow-y-auto",
            can_copy=True,
            border_radius="12px",
            use_transformers=True,
        ),
        class_name="relative mb-4",
        width="100%",
    )


def data_view() -> rx.Component:
    return rx.flex(
        code_block(PreviewState.json_data, "json"),
        rx.hstack(
            rx.button(
                rx.icon(tag="arrow-left"),
                "返回",
                on_click=rx.call_script("window.history.back()"),
                color_scheme="gray",
                variant="outline",
                radius="large",
                width="85px",
                height="40px",
                style={"cursor": "pointer"},
            ),
            rx.button(
                rx.icon(
                    tag="code-xml",
                ),
                "获取命令",
                on_click=PreviewState.get_code,
                color_scheme="iris",
                variant="outline",
                radius="large",
                width="140px",
                height="40px",
                style={"cursor": "pointer"},
            ),
            spacing="4",
        ),
        rx.cond(
            PreviewState.show_code,
            code_block(PreviewState.code, "bash"),
            rx.box(),
        ),
        direction="column",
        width="100%",
    )


@rx.page(route="/preview", on_load=PreviewState.load_json_data, title="弹幕预览")
@template
def preview() -> rx.Component:
    return rx.container(
        rx.vstack(
            rx.flex(
                rx.heading("JSON 预览", size="8"),
            ),
            rx.flex(
                rx.text(
                    "这是调取自后端接口的部分Json数据, 仅供参考, 请点击下方按钮获取调取完整数据的命令.",
                    size="4",
                    color_scheme="gray",
                ),
            ),
            rx.cond(
                PreviewState.loading,
                rx.center(
                    rx.vstack(
                        rx.spinner(color="red", size="3", class_name="animate-spin"),
                        rx.text(
                            "正在加载数据...",
                            class_name="text-gray-600 font-medium mt-3",
                        ),
                        align="center",
                        spacing="3",
                    ),
                    class_name="py-20",
                    width="100%",
                ),
                data_view(),
            ),
            width="100%",
            spacing="3",
            class_name="mt-6",
        ),
        width="100%",
        size="3",
        class_name="min-h-[calc(100vh-67px-145px)]",
    )
