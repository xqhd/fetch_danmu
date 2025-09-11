import reflex as rx


def navbar() -> rx.Component:
    return rx.box(
        rx.container(
            rx.flex(
                rx.flex(
                    rx.hstack(
                        rx.hstack(
                            rx.icon(
                                tag="youtube",
                                color=rx.color("red", 9),
                                size=28,
                            ),
                            rx.heading(
                                "弹幕搜索",
                                href="/",
                                size="6",
                                on_click=rx.redirect("/"),
                                class_name="bg-gradient-to-r from-red-500 to-orange-500 bg-clip-text text-transparent font-bold cursor-pointer",
                            ),
                            align="center",
                            spacing="3",
                        ),
                        rx.hstack(
                            rx.link(
                                "主页",
                                class_name="text-gray-600 hover:text-red-500 font-medium transition-colors duration-200 px-3 py-2 rounded-md hover:bg-gray-50",
                                underline="none",
                                href="/",
                            ),
                            rx.link(
                                "API文档",
                                class_name="text-gray-600 hover:text-red-500 font-medium transition-colors duration-200 px-3 py-2 rounded-md hover:bg-gray-50",
                                underline="none",
                                href="/docpage",
                            ),
                            align="center",
                            spacing="2",
                        ),
                        align="center",
                        spacing="8",
                    ),
                    align="center",
                ),
                rx.hstack(
                    rx.button(
                        rx.icon(
                            tag="github",
                            size=18,
                        ),
                        "Github",
                        on_click=rx.redirect(
                            "https://github.com/SeqCrafter/fetch_danmu",
                            is_external=True,
                        ),
                        class_name="px-4 py-2 bg-gray-900 hover:bg-gray-800 text-white font-medium rounded-lg transition-colors duration-200 shadow-sm hover:shadow-md",
                        variant="solid",
                        color_scheme="gray",
                        radius="large",
                        style={"cursor": "pointer"},
                    ),
                    rx.avatar(
                        src="/avata.png",
                        fallback="DM",
                        radius="full",
                        color_scheme="red",
                        size="4",
                        class_name="ring-2 ring-red-100 hover:ring-red-200 transition-all duration-200",
                    ),
                    align="center",
                    spacing="3",
                ),
                align="center",
                justify="between",
                height="35px",
                width="100%",
            ),
            size="4",
        ),
        width="100%",
        class_name="bg-white/80 backdrop-blur-md border-b border-gray-200/50 shadow-sm sticky top-0 z-50",
        style={"backdrop_filter": "blur(12px)"},
    )
