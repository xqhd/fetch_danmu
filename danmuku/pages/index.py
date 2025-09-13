import reflex as rx
from ..template import template
from ..provides.mtzy import search_vod_names
from ..components.search_media_cards import search_media_cards_component


class IndexState(rx.State):
    main_data: list[dict[str, str]] = []
    search_title: str = ""
    loading: bool = False

    @rx.event
    async def handle_key_events(self, event) -> None:
        if event == "Enter":
            if self.search_title == "":
                self.reset()
                yield
            else:
                self.loading = True
                self.main_data = await search_vod_names(self.search_title)
                self.loading = False
                yield

    @rx.event
    def clean_data(self) -> None:
        self.reset()


@rx.page(route="/", title="弹幕搜索")
@template
def index() -> rx.Component:
    return rx.box(
        rx.cond(
            IndexState.main_data.length() > 0,
            rx.container(
                rx.vstack(
                    rx.flex(
                        rx.box(
                            rx.input(
                                rx.input.slot(
                                    rx.icon(
                                        tag="search",
                                        size=20,
                                        class_name="text-gray-400",
                                    ),
                                ),
                                on_change=IndexState.set_search_title,
                                on_key_down=IndexState.handle_key_events,
                                variant="surface",
                                placeholder="搜索电影、电视剧、综艺节目...",
                                width="100%",
                                height="55px",
                                class_name="rounded-2xl bg-white/90 border border-gray-200 focus:border-red-400 focus:ring-4 focus:ring-red-100 transition-all duration-200 text-lg px-5 shadow-sm backdrop-blur-sm",
                            ),
                            rx.button(
                                rx.icon(tag="circle-x"),
                                on_click=IndexState.clean_data,
                                variant="ghost",
                                color_scheme="gray",
                                class_name="absolute right-4 top-4 cursor-pointer hover:bg-gray-100 rounded-full",
                            ),
                            width="100%",
                            max_width="600px",
                            class_name="relative bg-white/90 rounded-2xl",
                        ),
                        width="100%",
                        align="center",
                        justify="center",
                    ),
                    rx.cond(
                        IndexState.loading,
                        rx.center(
                            rx.vstack(
                                rx.spinner(
                                    color="red", size="3", class_name="animate-spin"
                                ),
                                rx.text(
                                    "正在搜索中...",
                                    class_name="text-gray-600 font-medium mt-3",
                                ),
                                align="center",
                                spacing="3",
                            ),
                            class_name="py-20",
                        ),
                        search_media_cards_component(main_data=IndexState.main_data),
                    ),
                    spacing="6",
                    width="100%",
                ),
                size="4",
                class_name="py-8",
            ),
            rx.container(
                rx.flex(
                    rx.vstack(
                        rx.vstack(
                            rx.heading(
                                "🎬 弹幕搜索",
                                size="9",
                                class_name="bg-gradient-to-r from-red-500 via-orange-500 to-pink-500 bg-clip-text text-transparent font-bold text-center",
                            ),
                            rx.text(
                                "搜索您喜爱的影视作品，获取弹幕数据",
                                size="4",
                                class_name="text-gray-600 text-center max-w-md",
                            ),
                            spacing="3",
                            align="center",
                            class_name="mb-8",
                        ),
                        rx.box(
                            rx.input(
                                rx.input.slot(
                                    rx.icon(
                                        tag="search",
                                        size=20,
                                        class_name="text-gray-400",
                                    ),
                                ),
                                on_change=IndexState.set_search_title,
                                on_key_down=IndexState.handle_key_events,
                                variant="surface",
                                placeholder="搜索电影、电视剧、综艺节目...",
                                width="100%",
                                height="55px",
                                class_name="rounded-2xl bg-white/90 border border-gray-200 focus:border-red-400 focus:ring-4 focus:ring-red-100 transition-all duration-200 text-lg px-5 shadow-sm backdrop-blur-sm",
                            ),
                            width="100%",
                            max_width="600px",
                            class_name="relative bg-white/90 rounded-2xl",
                        ),
                        rx.text(
                            "💡 支持搜索 Bilibili、爱奇艺、腾讯视频、优酷等平台内容",
                            size="3",
                            class_name="text-gray-500 text-center mt-4",
                        ),
                        spacing="4",
                        align="center",
                        width="100%",
                    ),
                    width="100%",
                    align="center",
                    justify="center",
                    justify_content="center",
                    class_name="h-[calc(100vh-67px-145px)] overflow-y-auto",
                ),
                size="4",
            ),
        ),
        class_name="min-h-[calc(100vh-67px-145px)] bg-gray-50",
    )
