import reflex as rx
from ..template import template
import os


class DocPageState(rx.State):
    api_doc: str = ""

    @rx.event
    def set_current_origin(self) -> None:
        origin_url = self.router.url.origin
        schema = self.router.url.scheme
        if schema == "https":
            ## using domain
            self.api_doc = f"{origin_url}/docs"
        else:
            backend_host = os.getenv("REFLEX_API_URL")
            self.api_doc = f"{backend_host}/docs"


@rx.page(route="/docpage", on_load=DocPageState.set_current_origin, title="API文档")
@template
def docpage() -> rx.Component:
    return rx.container(
        rx.el.iframe(
            src=DocPageState.api_doc,
            width="100%",
            height="500px",
        ),
        size="4",
        class_name="min-h-[calc(100vh-66px-70px)]",
    )
