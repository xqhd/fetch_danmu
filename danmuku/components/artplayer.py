import reflex as rx

artplayer_path = rx.asset("./artplayer.jsx", shared=True)


class ArtPlayer(rx.NoSSRComponent):
    library = f"$/public{artplayer_path}"

    lib_dependencies: list[str] = ["artplayer", "artplayer-plugin-danmuku", "hls.js"]

    tag = "ArtPlayerWithDanmaku"

    is_default = True

    ### props
    url: rx.Var[str] = ""
    danmaku_url: rx.Var[str] = ""


artplayer_component = ArtPlayer.create
