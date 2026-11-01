import inspect

from pyrogram.types import InlineKeyboardButton

import config

# newer pyrogram forks accept icon_custom_emoji_id on buttons; older ones don't
_ICON_OK = "icon_custom_emoji_id" in inspect.signature(
    InlineKeyboardButton.__init__
).parameters


def pbtn(text: str, name: str = None, **kwargs) -> InlineKeyboardButton:
    """Button with a premium emoji icon when an id is set and supported,
    otherwise a normal button showing `text`."""
    ids = getattr(config, "PREMIUM_EMOJI_IDS", {}) or {}
    eid = str(ids.get(name, "") or "").strip() if name else ""
    if eid and _ICON_OK:
        return InlineKeyboardButton(text=text, icon_custom_emoji_id=eid, **kwargs)
    return InlineKeyboardButton(text=text, **kwargs)
