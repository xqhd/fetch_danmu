import reflex as rx

config = rx.Config(
    app_name="danmuku",
    state_auto_setters=True,
    show_built_with_reflex=False,
    plugins=[
        rx.plugins.SitemapPlugin(),
        rx.plugins.TailwindV4Plugin(),
    ],
)
