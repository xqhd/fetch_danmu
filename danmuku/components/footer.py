import reflex as rx


def footer() -> rx.Component:
    return rx.box(
        rx.container(
            rx.flex(
                rx.vstack(
                    rx.hstack(
                        rx.icon(
                            tag="youtube",
                            color=rx.color("red", 6),
                            size=20,
                        ),
                        rx.text("弹幕搜索", class_name="text-gray-700 font-semibold"),
                        align="center",
                        spacing="2",
                    ),
                    rx.text(
                        "© 2025 danmuku. All for educations.",
                        class_name="text-gray-500 text-sm",
                    ),
                    rx.text(
                        "数据来源于第三方平台，仅供参考学习使用。",
                        class_name="text-gray-500 text-sm",
                    ),
                    spacing="2",
                    align="center",
                ),
                rx.vstack(
                    rx.text(
                        "友情链接",
                        class_name="text-gray-700 font-semibold text-sm mb-2",
                    ),
                    rx.hstack(
                        rx.link(
                            "GitHub",
                            href="https://github.com/SeqCrafter/fetch_danmu",
                            is_external=True,
                            class_name="text-gray-500 hover:text-red-500 text-sm transition-colors duration-200",
                        ),
                        rx.text("|", class_name="text-gray-300"),
                        rx.link(
                            "API 文档",
                            href="/docpage",
                            class_name="text-gray-500 hover:text-red-500 text-sm transition-colors duration-200",
                        ),
                        spacing="3",
                    ),
                    align="center",
                ),
                justify="between",
                align="center",
                class_name="flex-col lg:flex-row gap-4 lg:gap-0",
            ),
            size="4",
        ),
        class_name="bg-white border-t border-gray-200 py-4 mt-auto",
    )
