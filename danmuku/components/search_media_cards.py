import reflex as rx

localjs_path = rx.asset("./search_media_cards.jsx", shared=True)


class SearchMediaCards(rx.NoSSRComponent):
    library = f"$/public{localjs_path}"

    tag = "SearchMediaCards"

    is_default = True

    main_data: rx.Var[list[dict[str, str]]] = []


search_media_cards_component = SearchMediaCards.create
