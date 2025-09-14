import reflex as rx
from typing import Dict, Any

localjs_path = rx.asset("./douban_recommend_cards.jsx", shared=True)


class DoubanRecommendCards(rx.NoSSRComponent):
    library = f"$/public{localjs_path}"

    tag = "DoubanRecommendCards"

    is_default = True

    douban_data: rx.Var[Dict[str, Any]] = {}

    on_card_click: rx.EventHandler[rx.event.passthrough_event_spec(str)]


douban_recommend_cards_component = DoubanRecommendCards.create
