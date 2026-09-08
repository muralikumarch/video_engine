from PIL import Image, ImageDraw, ImageFont
import os


def _get_font(size):
    """Fallback font loader for Windows and Linux environments."""
    windows_fonts = ["C:\\Windows\\Fonts\\segoeui.ttf", "C:\\Windows\\Fonts\\arial.ttf"]
    for font_path in windows_fonts:
        if os.path.exists(font_path):
            try:
                return ImageFont.truetype(font_path, size)
            except Exception:
                pass
    return ImageFont.load_default()


def render_bullet_slide(data, output_path, theme):
    width, height = 1920, 1080

    bg = tuple(theme.get("bg_color", [20, 24, 33]))
    card = tuple(theme.get("card_color", [30, 36, 50]))
    accent = tuple(theme.get("accent_color", [56, 189, 248]))
    alert = tuple(theme.get("alert_color", [239, 68, 68]))
    text_main = tuple(theme.get("text_main", [240, 244, 250]))
    text_muted = tuple(theme.get("text_muted", [156, 163, 175]))

    img = Image.new("RGB", (width, height), bg)
    draw = ImageDraw.Draw(img)

    font_title = _get_font(46)
    font_sub = _get_font(26)
    font_bullet = _get_font(28)
    font_subbullet = _get_font(24)

    # Accent Header Bar
    draw.rectangle([(80, 60), (1840, 68)], fill=accent)
    draw.text((80, 95), data.get("title", ""), fill=accent, font=font_title)
    draw.text((80, 165), data.get("subtitle", ""), fill=text_muted, font=font_sub)

    # Main Card
    draw.rounded_rectangle([(80, 230), (1840, 980)], radius=16, fill=card)

    y = 280
    for item in data.get("items", []):
        if item.startswith("[!]"):
            draw.text((120, y), item[4:], fill=alert, font=font_bullet)
        elif item.startswith("[+]"):
            draw.text((120, y), item[4:], fill=accent, font=font_bullet)
        elif item.startswith("    "):
            draw.text((160, y), item[4:], fill=text_muted, font=font_subbullet)
        else:
            draw.text((120, y), item, fill=text_main, font=font_bullet)
        y += 48

    img.save(output_path, "PNG")
