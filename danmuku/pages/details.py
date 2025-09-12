import reflex as rx
from ..template import template
from ..provides.mtzy import get_vod_details
from typing import Any, Dict, List


class DetailsState(rx.State):
    vod_details: Dict[str, Any] = {}
    episode_list: Dict[str, Dict[str, str]] = {}
    default_value: str = ""
    loading: bool = True

    @rx.event
    async def load_json_data(self) -> None:
        args = self.router.url.query_parameters
        vod_id = args.get("vod_id", "")
        if vod_id:
            self.vod_details = await get_vod_details(int(vod_id))
            self.episode_list = self.vod_details["list"]
            self.default_value = list(self.vod_details["list"].keys())[0]
            self.loading = False
            yield
        else:
            rx.redirect("/")

    @rx.event
    def unmount_clean(self) -> None:
        self.reset()


def single_episode_box(episode_number: str, episode_url: str) -> rx.Component:
    return rx.link(
        rx.box(
            rx.text(
                episode_number,
                class_name="text-center font-medium text-gray-700 group-hover:text-red-600 transition-colors duration-200",
            ),
            class_name="w-12 h-10 border border-gray-200 rounded-lg flex items-center justify-center bg-white hover:bg-red-50 hover:border-red-300 transition-all duration-200 group cursor-pointer shadow-sm hover:shadow-md",
        ),
        href=f"/preview?url={episode_url}&douban_id={DetailsState.vod_details['vod_douban_id']}&episode_number={episode_number}",
        class_name="group",
    )


def episode_list(item: List) -> rx.Component:
    return (
        rx.flex(
            rx.foreach(
                item,
                lambda item: single_episode_box(item[0], item[1]),
            ),
            spacing="3",
            flex_wrap="wrap",
            class_name="p-6 bg-gray-50 rounded-xl",
        ),
    )


def mutisource_episode_list(source_data: List, default_value: str) -> rx.Component:
    return rx.tabs.root(
        rx.tabs.list(
            rx.foreach(
                source_data,
                lambda item: rx.tabs.trigger(
                    item[0],
                    value=item[0],
                    class_name="px-4 py-2 rounded-lg font-medium text-gray-600 hover:text-red-600 hover:bg-red-50 transition-all duration-200 data-[state=active]:bg-red-100 data-[state=active]:text-red-700 data-[state=active]:font-semibold",
                ),
            ),
            class_name="flex flex-wrap gap-2 mb-4",
        ),
        rx.foreach(
            source_data,
            lambda item: rx.tabs.content(
                episode_list(item[1]), value=item[0], class_name="focus:outline-none"
            ),
        ),
        default_value=default_value,
        class_name="w-full",
    )


@rx.page(route="/details", on_load=DetailsState.load_json_data, title="影视详情")
@template
def details() -> rx.Component:
    return rx.box(
        rx.cond(
            DetailsState.loading,
            rx.center(
                rx.vstack(
                    rx.spinner(color="red", size="3", class_name="animate-spin"),
                    rx.text(
                        "正在加载详情...", class_name="text-gray-600 font-medium mt-3"
                    ),
                    align="center",
                    spacing="3",
                ),
                class_name="py-20",
            ),
            rx.container(
                rx.vstack(
                    rx.card(
                        rx.flex(
                            rx.box(
                                rx.image(
                                    src=DetailsState.vod_details["vod_pic"],
                                    class_name="w-64 h-96 object-cover rounded-xl shadow-lg",
                                ),
                                flex_shrink="0",
                            ),
                            rx.vstack(
                                rx.heading(
                                    DetailsState.vod_details["vod_name"],
                                    size="7",
                                    class_name="text-gray-800 font-bold mb-4",
                                ),
                                rx.vstack(
                                    rx.hstack(
                                        rx.text(
                                            "类型：",
                                            class_name="text-gray-500 font-medium min-w-[60px]",
                                        ),
                                        rx.badge(
                                            DetailsState.vod_details["vod_class"],
                                            color_scheme="red",
                                            variant="soft",
                                            radius="full",
                                        ),
                                        align="center",
                                        spacing="2",
                                    ),
                                    rx.hstack(
                                        rx.text(
                                            "标签：",
                                            class_name="text-gray-500 font-medium min-w-[60px]",
                                        ),
                                        rx.text(
                                            DetailsState.vod_details["vod_tag"],
                                            class_name="text-gray-700",
                                        ),
                                        align="start",
                                        spacing="2",
                                    ),
                                    rx.hstack(
                                        rx.text(
                                            "演员：",
                                            class_name="text-gray-500 font-medium min-w-[60px]",
                                        ),
                                        rx.text(
                                            DetailsState.vod_details["vod_actor"],
                                            class_name="text-gray-700 line-clamp-2",
                                        ),
                                        align="start",
                                        spacing="2",
                                    ),
                                    rx.hstack(
                                        rx.text(
                                            "导演：",
                                            class_name="text-gray-500 font-medium min-w-[60px]",
                                        ),
                                        rx.text(
                                            DetailsState.vod_details["vod_director"],
                                            class_name="text-gray-700",
                                        ),
                                        align="start",
                                        spacing="2",
                                    ),
                                    rx.hstack(
                                        rx.text(
                                            "发布：",
                                            class_name="text-gray-500 font-medium min-w-[60px]",
                                        ),
                                        rx.text(
                                            DetailsState.vod_details["vod_pubdate"],
                                            class_name="text-gray-700",
                                        ),
                                        align="start",
                                        spacing="2",
                                    ),
                                    spacing="3",
                                    align="start",
                                    width="100%",
                                ),
                                rx.box(
                                    rx.text(
                                        "剧情简介",
                                        class_name="text-gray-500 font-medium mb-2",
                                    ),
                                    rx.text(
                                        DetailsState.vod_details["vod_description"],
                                        class_name="text-gray-700 leading-relaxed",
                                    ),
                                    class_name="mt-4 p-4 bg-gray-50 rounded-lg",
                                ),
                                spacing="4",
                                align="start",
                                width="100%",
                            ),
                            spacing="6",
                            align="start",
                            class_name="flex-col lg:flex-row",
                        ),
                        class_name="p-6 bg-white rounded-2xl shadow-sm border border-gray-200",
                    ),
                    rx.card(
                        rx.vstack(
                            rx.hstack(
                                rx.icon(
                                    tag="loader-circle",
                                    size=24,
                                    class_name="text-red-500",
                                ),
                                rx.heading(
                                    "剧集列表",
                                    size="5",
                                    class_name="text-gray-800 font-bold",
                                ),
                                align="center",
                                spacing="3",
                            ),
                            mutisource_episode_list(
                                DetailsState.episode_list, DetailsState.default_value
                            ),
                            spacing="4",
                            width="100%",
                        ),
                        class_name="p-6 bg-white rounded-2xl shadow-sm border border-gray-200",
                    ),
                    spacing="6",
                    width="100%",
                    class_name="py-8",
                ),
                size="4",
                on_unmount=DetailsState.unmount_clean,
            ),
        ),
        class_name="min-h-[calc(100vh-70px-64px)] bg-gray-50",
    )
