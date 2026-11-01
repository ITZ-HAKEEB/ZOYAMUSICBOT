import os
import random
import re
import aiohttp
import aiofiles
from functools import lru_cache
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

# ═══════════════════════════════════════════════════════════════════
# THUMBNAIL GENERATOR - VERSION 6 (Glass Card + Vertical Progress)
# Layout: blurred bg, glass rounded card, vertical time bar on the left,
# title + "channel | views" below the card. Fonts are the bot's own.
# ═══════════════════════════════════════════════════════════════════

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(BASE_DIR, "..", "assets")
FONT_TITLE = os.path.join(ASSETS, "f.ttf")          # Honey Salt (title)
FONT_META = os.path.join(ASSETS, "font.ttf")        # Poppins SemiBold (meta / time)
FONT_BOLD = os.path.join(ASSETS, "Poppins-Bold.ttf")  # Poppins Bold (watermarks)

W, H = 1280, 720

# ---- layout ----------------------------------------------------------------
PANEL = (197, 20, 1083, 580)     # faint dark panel behind the card
CARD = (237, 60, 1043, 540)      # glass card
CARD_R = 52
ART = (267, 90, 1013, 510)       # artwork inside the card (746 x 420)
ART_R = 40
BAR_X, BAR_Y1, BAR_Y2, BAR_W = 128, 90, 510, 16   # vertical progress bar
TITLE_POS = (267, 566)
META_POS = (267, 608)
TITLE_MAX_W = 740

# ---- colours ---------------------------------------------------------------
BAR_TRACK = (160, 158, 165, 235)
TEXT_WHITE = (255, 255, 255)

# neon palette - a different one is picked every time a thumbnail is made
NEON_COLORS = [
    (57, 255, 20),     # neon green
    (0, 240, 255),     # cyan
    (255, 20, 147),    # hot pink
    (255, 0, 255),     # magenta
    (176, 38, 255),    # purple
    (255, 95, 31),     # neon orange
    (255, 240, 31),    # neon yellow
    (30, 144, 255),    # electric blue
    (255, 49, 49),     # neon red
    (0, 255, 170),     # aqua green
]
_last_color = None


def _pick_neon():
    global _last_color
    choices = [c for c in NEON_COLORS if c != _last_color] or NEON_COLORS
    _last_color = random.choice(choices)
    return _last_color

# ---- text ------------------------------------------------------------------
FALLBACK_THUMB = "https://o.uguu.se/snWhWXPT.jpg"

_thumb_memory: dict = {}  # videoid -> output_path


@lru_cache(maxsize=16)
def _font(path: str, size: int) -> ImageFont.FreeTypeFont:
    for p in (path, FONT_META, FONT_TITLE):
        try:
            return ImageFont.truetype(p, size)
        except Exception:
            continue
    return ImageFont.load_default()


def _truncate(draw, text, font, max_w):
    if draw.textlength(text, font=font) <= max_w:
        return text
    while text and draw.textlength(text + "...", font=font) > max_w:
        text = text[:-1]
    return text.rstrip() + "..."


def _cover(img: Image.Image, w: int, h: int) -> Image.Image:
    """Resize + centre-crop so the image fully covers w x h."""
    iw, ih = img.size
    scale = max(w / iw, h / ih)
    nw, nh = int(iw * scale) + 1, int(ih * scale) + 1
    img = img.resize((nw, nh), Image.LANCZOS)
    left, top = (nw - w) // 2, (nh - h) // 2
    return img.crop((left, top, left + w, top + h))


def _rounded_mask(size, radius, scale=4):
    """Anti-aliased rounded-rectangle mask."""
    w, h = size
    m = Image.new("L", (w * scale, h * scale), 0)
    ImageDraw.Draw(m).rounded_rectangle(
        [0, 0, w * scale - 1, h * scale - 1], radius=radius * scale, fill=255
    )
    return m.resize((w, h), Image.LANCZOS)


def _make_bg(song_img: Image.Image, neon) -> Image.Image:
    bg = _cover(song_img.convert("RGB"), W, H).filter(ImageFilter.GaussianBlur(45))
    bg = ImageEnhance.Brightness(bg).enhance(0.6)
    bg = ImageEnhance.Color(bg).enhance(0.8).convert("RGBA")

    # soft violet-grey tint + faint dark panel behind the card
    bg = Image.alpha_composite(bg, Image.new("RGBA", (W, H), (*neon, 85)))
    panel = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(panel).rectangle(PANEL, fill=(10, 8, 16, 70))
    return Image.alpha_composite(bg, panel)


def _draw_card(base: Image.Image, neon) -> Image.Image:
    x1, y1, x2, y2 = CARD
    base = base.convert("RGBA")

    # soft glow around the card
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(glow).rounded_rectangle(
        [x1 - 6, y1 - 6, x2 + 6, y2 + 6], radius=CARD_R + 6, fill=(*neon, 190)
    )
    base = Image.alpha_composite(base, glow.filter(ImageFilter.GaussianBlur(22)))

    # frosted-glass body + light border
    glass = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glass)
    gd.rounded_rectangle(CARD, radius=CARD_R, fill=(*neon, 50))
    gd.rounded_rectangle(CARD, radius=CARD_R, outline=(*neon, 235), width=3)
    return Image.alpha_composite(base, glass).convert("RGB")


def _paste_art(base: Image.Image, song_img: Image.Image, neon) -> Image.Image:
    x1, y1, x2, y2 = ART
    w, h = x2 - x1, y2 - y1
    art = _cover(song_img.convert("RGB"), w, h)

    # soft inner glow under the art
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(glow).rounded_rectangle(ART, radius=ART_R, fill=(*neon, 200))
    base = Image.alpha_composite(
        base.convert("RGBA"), glow.filter(ImageFilter.GaussianBlur(14))
    ).convert("RGB")

    base.paste(art, (x1, y1), _rounded_mask((w, h), ART_R))
    return base


def _draw_bar(base: Image.Image, neon, progress: float = 0.06) -> Image.Image:
    """Vertical progress bar (fills from the bottom)."""
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    r = BAR_W // 2
    d.rounded_rectangle([BAR_X, BAR_Y1, BAR_X + BAR_W, BAR_Y2], radius=r, fill=BAR_TRACK)
    fill_h = max(BAR_W, int((BAR_Y2 - BAR_Y1) * progress))
    d.rounded_rectangle(
        [BAR_X, BAR_Y2 - fill_h, BAR_X + BAR_W, BAR_Y2], radius=r, fill=(*neon, 255)
    )
    return Image.alpha_composite(base.convert("RGBA"), layer).convert("RGB")


async def get_thumb(videoid: str, user_name: str = None) -> str:
    output = f"cache/{videoid}.png"
    cache = f"cache/thumb{videoid}.jpg"
    os.makedirs("cache", exist_ok=True)

    # always regenerate so the player/views stay fresh
    if os.path.exists(output):
        try:
            os.remove(output)
        except Exception:
            pass

    # 1) metadata
    url = f"https://www.youtube.com/watch?v={videoid}"
    try:
        from py_yt import VideosSearch

        data = (await VideosSearch(url, limit=1).next())["result"][0]
        title = re.sub(r"[\x00-\x1f\x7f]", "", data.get("title", "Unknown")).strip()
        duration = data.get("duration", "00:00") or "00:00"
        thumb_url = data.get("thumbnails", [{}])[-1].get("url", "").split("?")[0]
        v_raw = str((data.get("viewCount") or {}).get("short", "N/A"))
        vc = re.sub(r"\s*views?\s*", "", v_raw, flags=re.IGNORECASE).strip()
        channel = ((data.get("channel") or {}).get("name") or "Unknown").strip()
    except Exception:
        return FALLBACK_THUMB

    # 2) artwork
    try:
        async with aiohttp.ClientSession() as sess:
            async with sess.get(thumb_url, timeout=aiohttp.ClientTimeout(total=10)) as r:
                async with aiofiles.open(cache, "wb") as f:
                    await f.write(await r.read())
        song_img = Image.open(cache).convert("RGB")
    except Exception:
        song_img = Image.new("RGB", (777, 458), (28, 10, 5))

    # 3) compose
    neon = _pick_neon()
    base = _make_bg(song_img, neon).convert("RGB")
    base = _draw_card(base, neon)
    base = _paste_art(base, song_img, neon)
    base = _draw_bar(base, neon)
    draw = ImageDraw.Draw(base)

    f_title = _font(FONT_TITLE, 34)
    f_meta = _font(FONT_META, 26)
    f_time = _font(FONT_META, 28)

    # time labels around the vertical bar (total on top, elapsed at bottom)
    cx = BAR_X + BAR_W // 2
    draw.text((cx, 70), duration, font=f_time, fill=TEXT_WHITE, anchor="mm")
    draw.text((cx, 541), "00:00", font=f_time, fill=TEXT_WHITE, anchor="mm")

    # title + "channel | views" (left aligned under the card)
    title_text = _truncate(draw, title, f_title, TITLE_MAX_W)
    draw.text((TITLE_POS[0] + 2, TITLE_POS[1] + 2), title_text, font=f_title, fill=(0, 0, 0), anchor="lm")
    draw.text(TITLE_POS, title_text, font=f_title, fill=TEXT_WHITE, anchor="lm")

    meta = _truncate(draw, f"{channel} | {vc} views", f_meta, TITLE_MAX_W)
    draw.text(META_POS, meta, font=f_meta, fill=TEXT_WHITE, anchor="lm")

    base.save(output, "PNG", optimize=True)

    try:
        if os.path.exists(cache):
            os.remove(cache)
    except Exception:
        pass

    _thumb_memory[videoid] = output
    return output
