import reflex as rx
from .api import fastapi_app

app = rx.App(
    theme=rx.theme(
        appearance="light",
        has_background=True,
    ),
    api_transformer=fastapi_app,
)
