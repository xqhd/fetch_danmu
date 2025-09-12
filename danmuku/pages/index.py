import reflex as rx
from ..template import template
from ..provides.caiji import search_vod_names


class IndexState(rx.State):
    main_data: list[dict[str, str]] = []
    paginated_data: list[dict[str, str]] = []

    limits: list[str] = ["6", "12", "18", "24", "30"]

    current_limit: int = 6
    offset: int = 0
    current_page: int = 1
    number_of_rows: int = 0
    total_pages: int = 0
    search_title: str = ""
    loading: bool = False

    @rx.event
    async def handle_key_events(self, event) -> None:
        if event == "Enter":
            if self.search_title == "":
                self.main_data = []
                self.number_of_rows = 0
                self.total_pages = 0
                yield
            else:
                self.loading = True
                await self.set_main_data()
                self.loading = False
                self.search_title = ""
                yield

    async def set_main_data(self) -> None:
        self.main_data = await search_vod_names(self.search_title)
        self.number_of_rows = len(self.main_data)
        self.total_pages = (
            self.number_of_rows + self.current_limit - 1
        ) // self.current_limit
        self.paginate()

    @rx.event
    def paginate(self) -> None:
        start = self.offset
        end = start + self.current_limit
        self.paginated_data = self.main_data[start:end]
        self.current_page = (self.offset // self.current_limit) + 1

    @rx.event
    def delta_limit(self, limit: str) -> None:
        self.current_limit = int(limit)
        self.offset = 0
        self.total_pages = (
            self.number_of_rows + self.current_limit - 1
        ) // self.current_limit
        self.paginate()

    @rx.event
    def previous(self) -> None:
        if self.offset >= self.current_limit:
            self.offset -= self.current_limit
        else:
            self.offset = 0

        self.paginate()

    @rx.event
    def next(self) -> None:
        if self.offset + self.current_limit < self.number_of_rows:
            self.offset += self.current_limit

        self.paginate()

    @rx.event
    def unmount_clean(self) -> None:
        self.reset()


#############components#################
def search_box() -> rx.Component:
    return rx.flex(
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
                        rx.icon(tag="search", size=20, class_name="text-gray-400"),
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
    )


def search_box_2() -> rx.Component:
    return rx.flex(
        rx.box(
            rx.input(
                rx.input.slot(
                    rx.icon(tag="search", size=20, class_name="text-gray-400"),
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
        width="100%",
        align="center",
        justify="center",
    )


def media_card(
    vod_id: str, title: str, vod_class: str, vod_pubdate: str, vod_pic: str
) -> rx.Component:
    return rx.card(
        rx.flex(
            rx.vstack(
                rx.heading(
                    title,
                    size="4",
                    class_name="text-gray-800 font-semibold line-clamp-2 overflow-hidden",
                ),
                rx.vstack(
                    rx.badge(
                        vod_class,
                        color_scheme="red",
                        variant="soft",
                        radius="full",
                        class_name="text-xs max-w-[200px] truncate",
                    ),
                    rx.text(vod_pubdate, size="2", class_name="text-gray-500"),
                    align="start",
                    spacing="2",
                    width="100%",
                ),
                spacing="3",
                align="start",
                width="100%",
            ),
            rx.box(
                rx.image(
                    src=vod_pic,
                    width="90px",
                    height="110px",
                    class_name="rounded-lg object-cover shadow-sm",
                ),
                flex_shrink="0",
            ),
            justify="between",
            align_items="center",
            align="start",
            width="100%",
            spacing="4",
        ),
        on_click=rx.redirect(f"/details?vod_id={vod_id}"),
        class_name="p-3 bg-white border border-gray-200 rounded-xl hover:shadow-lg hover:-translate-y-1 transition-all duration-300 cursor-pointer hover:border-red-200 group",
    )


def pagination() -> rx.Component:
    return rx.hstack(
        rx.hstack(
            rx.text("每页显示", class_name="text-gray-600 font-medium text-sm"),
            rx.select(
                IndexState.limits,
                default_value="6",
                on_change=IndexState.delta_limit,
                class_name="bg-white border border-gray-200 rounded-lg px-3 py-1 text-sm focus:border-red-400 focus:ring-2 focus:ring-red-100",
                width="80px",
            ),
            rx.text("条", class_name="text-gray-600 font-medium text-sm"),
            align_items="center",
            spacing="2",
        ),
        rx.hstack(
            rx.text(
                f"第 {IndexState.current_page} 页，共 {IndexState.total_pages} 页",
                class_name="text-gray-600 font-medium text-sm min-w-[120px] text-center",
            ),
            rx.button(
                rx.icon(
                    tag="chevron-left",
                    size=16,
                ),
                on_click=IndexState.previous,
                class_name="bg-white border border-gray-200 hover:border-red-300 hover:bg-red-50 transition-all duration-200 rounded-lg",
                variant="surface",
                size="2",
                width="36px",
                height="36px",
                style={"cursor": "pointer"},
            ),
            rx.button(
                rx.icon(
                    tag="chevron-right",
                    size=16,
                ),
                on_click=IndexState.next,
                class_name="bg-white border border-gray-200 hover:border-red-300 hover:bg-red-50 transition-all duration-200 rounded-lg",
                variant="surface",
                size="2",
                width="36px",
                height="36px",
                style={"cursor": "pointer"},
            ),
            align_items="center",
            spacing="2",
        ),
        align_items="center",
        spacing="6",
        flex_wrap="wrap",
        class_name="bg-white rounded-lg p-3 shadow-sm border border-gray-200",
    )


def search_result() -> rx.Component:
    return rx.flex(
        rx.hstack(
            rx.heading("搜索结果", size="6", class_name="text-gray-800 font-bold"),
            rx.text(
                f"找到 {IndexState.number_of_rows} 个结果",
                class_name="text-gray-500 font-medium",
            ),
            align="center",
            spacing="3",
        ),
        rx.grid(
            rx.foreach(
                IndexState.paginated_data,
                lambda item: media_card(
                    item["vod_id"],
                    item["vod_name"],
                    item["vod_class"],
                    item["vod_pubdate"],
                    item["vod_pic"],
                ),
            ),
            columns="1",
            spacing="4",
            width="100%",
            class_name="md:grid-cols-2",
        ),
        rx.flex(
            pagination(),
            width="100%",
            justify="center",
        ),
        direction="column",
        width="100%",
        spacing="6",
    )


@rx.page(route="/", title="弹幕搜索")
@template
def index() -> rx.Component:
    return rx.box(
        rx.cond(
            IndexState.total_pages > 0,
            rx.container(
                rx.vstack(
                    search_box_2(),
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
                        search_result(),
                    ),
                    spacing="6",
                    width="100%",
                ),
                size="4",
                class_name="py-8",
            ),
            rx.container(
                search_box(),
                size="4",
            ),
        ),
        on_unmount=IndexState.unmount_clean,
        class_name="min-h-[calc(100vh-67px-145px)] bg-gray-50",
    )
