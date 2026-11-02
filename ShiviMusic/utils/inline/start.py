# ===========================================================
# ©️ 2025-26 All Rights Reserved by Purvi Bots (Im-Notcoder) 🚀
#
# This source code is under MIT License 📜
# ===========================================================

import inspect
from pyrogram import enums
from pyrogram.types import InlineKeyboardButton

import config
from ShiviMusic import app

# Check if the installed pyrogram/fork natively accepts icon_custom_emoji_id
_SUPPORTS_ICON = "icon_custom_emoji_id" in inspect.signature(
    InlineKeyboardButton.__init__
).parameters


def _btn(text: str, icon_custom_emoji_id: str = None, **kwargs) -> InlineKeyboardButton:
    """Create an InlineKeyboardButton with custom emoji ID support when available."""
    if icon_custom_emoji_id and _SUPPORTS_ICON:
        return InlineKeyboardButton(text=text, icon_custom_emoji_id=str(icon_custom_emoji_id), **kwargs)
    btn = InlineKeyboardButton(text=text, **kwargs)
    if icon_custom_emoji_id:
        try:
            setattr(btn, "icon_custom_emoji_id", str(icon_custom_emoji_id))
        except Exception:
            pass
    return btn


# ===========================================================
# START PANEL
# ===========================================================

def start_panel(_):

    buttons = [
        [
            _btn(
                text=f"✈️ {_['S_B_1']} ➡️",
                url=f"https://t.me/{app.username}?startgroup=true",
                style=enums.ButtonStyle.PRIMARY,
                icon_custom_emoji_id="5875465628285931233",
            ),
            _btn(
                text=f"💬 {_['S_B_2']}",
                url=config.SUPPORT_CHAT,
                style=enums.ButtonStyle.SUCCESS,
                icon_custom_emoji_id="5843826335088120045",
            ),
        ],
    ]

    return buttons


# ===========================================================
# PRIVATE PANEL
# ===========================================================

def private_panel(_):

    buttons = [
        [
            _btn(
                text="✈️ ʌᴅᴅ ϻє ɪη ʏσυʀ ɢʀσυᴘ ➡️",
                url=f"https://t.me/{app.username}?startgroup=true",
                style=enums.ButtonStyle.PRIMARY,
                icon_custom_emoji_id="5875465628285931233",
            )
        ],
        [
            _btn(
                text="👤 ˹ ❍ᴡηєʀ ˼",
                user_id=config.OWNER_ID,
                style=enums.ButtonStyle.DANGER,
                icon_custom_emoji_id="5879770735999717115",
            ),
            _btn(
                text="💬 ˹ sυᴘᴘσʀᴛ ˼",
                url=config.SUPPORT_CHAT,
                style=enums.ButtonStyle.SUCCESS,
                icon_custom_emoji_id="5843826335088120045",
            ),
        ],
        [
            _btn(
                text="🔓 ˹ ʜєʟᴘ ᴧηᴅ ᴄσϻϻᴧηᴅs ˼ ➡️",
                callback_data="settings_back_helper",
                style=enums.ButtonStyle.PRIMARY,
                icon_custom_emoji_id="5886505193180239900",
            )
        ],
    ]

    return buttons


# ===========================================================
# ©️ 2025-26 All Rights Reserved by Purvi Bots (Im-Notcoder)
#
# 🧑‍💻 Developer : t.me/TheSigmaCoder
# 🔗 Source link : GitHub.com/Im-Notcoder/Shivi-V2
# 📢 Telegram channel : t.me/Purvi_Bots
# ===========================================================
