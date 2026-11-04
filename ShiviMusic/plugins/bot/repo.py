from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from ShiviMusic import app
from config import BOT_USERNAME

start_txt = """**
<u>❃ ᴡєʟᴄσϻє ᴛᴏ ᴛєᴧϻ ɴᴏʙɪ ʀєᴘσs ❃</u>
 
✼ ʀєᴘᴏ ɪs ηᴏᴡ ᴘʀɪᴠᴧᴛє ᴅᴜᴅє 😌
 
❉  ʏᴏᴜ ᴄᴧη мʏ ᴜsє ᴘᴜʙʟɪᴄ ʀєᴘσs !!  

✼ || [˹ɴᴏʙɪ ꭙ ʙᴏᴛѕ˼ 💞](https://t.me/llNOBI_SUPPORTll) ||
 
❊ ʀᴜη 24x7 ʟᴧɢ ϝʀєє ᴡɪᴛʜσᴜᴛ sᴛσᴘ**
"""


@app.on_message(filters.command("repo"))
async def repo_command(_, msg):
    buttons = [
        [
            InlineKeyboardButton("✙ ᴧᴅᴅ ϻє вᴧʙʏ ✙", url=f"https://t.me/{BOT_USERNAME}?startgroup=true")
        ],
        [
            InlineKeyboardButton("• ʜєʟᴘ •", url="https://t.me/llNOBI_SUPPORTll"),
            InlineKeyboardButton("• 𝛅ᴜᴘᴘσʀᴛ •", url="https://t.me/llNOBI_SUPPORTll"),
        ],
        [
            InlineKeyboardButton("• ϻᴧɪη ʙσᴛ •", url="https://t.me/{BOT_USERNAME}?startgroup=true"),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(buttons)
    await msg.reply_photo(
        photo="https://kommodo.ai/i/VBGCtCxoFhN6o0sdZAU8",
        caption=start_txt,
        reply_markup=reply_markup,
    )
