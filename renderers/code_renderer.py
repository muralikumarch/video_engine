from PIL import Image, ImageDraw, ImageFont
import os


def _get_font(size):
    fonts = [
        "C:\\Windows\\Fonts\\consola.ttf",
        "C:\\Windows\\Fonts\\cour.ttf",
        "C:\\Windows\\Fonts\\arial.ttf",
    ]
    for font_path in fonts:
        if os.path.exists(font_path):
            try:
                return ImageFont.truetype(font_path, size)
            except Exception:
                pass
    return ImageFont.load_default()


def render_code_slide(data, output_path, theme):
    width, height = 1920, 1080

    bg = tuple(theme.get("bg_color", [20, 24, 33]))
    accent = tuple(theme.get("accent_color", [56, 189, 248]))
    text_main = tuple(theme.get("text_main", [240, 244, 250]))
    text_muted = tuple(theme.get("text_muted", [156, 163, 175]))

    img = Image.new("RGB", (width, height), bg)
    draw = ImageDraw.Draw(img)

    font_title = _get_font(46)
    font_sub = _get_font(26)
    font_code = _get_font(24)

    # Header
    draw.rectangle([(80, 60), (1840, 68)], fill=accent)
    draw.text(
        (80, 95), data.get("title", "CODE IMPLEMENTATION"), fill=accent, font=font_title
    )
    draw.text((80, 165), data.get("subtitle", ""), fill=text_muted, font=font_sub)

    # IDE Terminal Frame
    draw.rounded_rectangle([(80, 230), (1840, 980)], radius=16, fill=(15, 18, 26))

    # macOS/Editor Window Buttons
    draw.ellipse([(115, 255), (131, 271)], fill=(239, 68, 68))
    draw.ellipse([(141, 255), (157, 271)], fill=(234, 179, 8))
    draw.ellipse([(167, 255), (183, 271)], fill=(34, 197, 94))

    code_lines = data.get("code", [])
    y = 310
    keywords = [
        "@",
        "class ",
        "public ",
        "return ",
        "CompletableFuture",
        "List<",
        "void ",
        "import ",
    ]

    for idx, line in enumerate(code_lines, start=1):
        # Line numbers
        draw.text((120, y), f"{idx:2d}", fill=(80, 90, 110), font=font_code)

        # Syntax styling
        color = accent if any(k in line for k in keywords) else text_main
        if line.strip().startswith("//"):
            color = text_muted

        draw.text((180, y), line, fill=color, font=font_code)
        y += 40

    img.save(output_path, "PNG")
