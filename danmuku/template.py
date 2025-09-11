from typing import Callable

import reflex as rx

from .components.navbar import navbar
from .components.footer import footer


def template(
    page: Callable[[], rx.Component],
) -> rx.Component:
    return rx.flex(
        navbar(),
        page(),
        footer(),
        direction="column",
        min_height="100vh",
        width="100%",
        class_name="bg-gray-50",
    )
