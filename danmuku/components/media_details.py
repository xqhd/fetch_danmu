import reflex as rx
from typing import Dict, Any

artplayer_path = rx.asset("./media_details.jsx", shared=True)


class MediaDetails(rx.NoSSRComponent):
    library = f"$/public{artplayer_path}"

    tag = "MediaDetails"

    is_default = True

    vod_details: rx.Var[Dict[str, Any]] = {}


media_details_component = MediaDetails.create
