"""
Generate animated GIF spider states from source image.

Run: python assets/generate_spider_gifs.py
Produces: spider_idle.gif, spider_crawling.gif, spider_thinking.gif, spider_happy.gif,
          spider_wave.gif, spider_jump.gif, spider_spin.gif, spider_nod.gif
"""

import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ASSETS_DIR = Path(__file__).parent
SOURCE = ASSETS_DIR / "spider_source.jpg"
TARGET_SIZE = 200


def remove_background(img):
    """Remove light gray/white background, make transparent."""
    img = img.convert("RGBA")
    data = img.getdata()
    new_data = []
    for item in data:
        r, g, b, a = item
        if r > 200 and g > 200 and b > 200:
            new_data.append((255, 255, 255, 0))
        else:
            new_data.append((r, g, b, a))
    img.putdata(new_data)
    return img


def crop_to_content(img):
    """Crop transparent pixels, keep only the spider."""
    bbox = img.getbbox()
    if bbox:
        img = img.crop(bbox)
    return img


def fit_to_size(img, size):
    """Fit image into size x size canvas, centered."""
    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    w, h = img.size
    scale = min(size / w, size / h) * 0.85
    new_w, new_h = int(w * scale), int(h * scale)
    img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
    x = (size - new_w) // 2
    y = (size - new_h) // 2
    canvas.paste(img, (x, y), img)
    return canvas


def draw_thought_bubbles(draw, cx, top_y, frame, total):
    """Draw 3 thought bubbles that grow."""
    phase = (frame % total) / total
    bubbles = [
        (cx + 30, top_y - 15, 5),
        (cx + 42, top_y - 30, 7),
        (cx + 50, top_y - 48, 4),
    ]
    for i, (bx, by, max_r) in enumerate(bubbles):
        progress = (phase + i * 0.3) % 1.0
        r = max_r * (0.5 + 0.5 * math.sin(progress * math.pi * 2))
        if r < 1:
            r = 1
        alpha = int(180 * (0.5 + 0.5 * math.sin(progress * math.pi * 2)))
        draw.ellipse(
            [bx - r, by - r, bx + r, by + r],
            fill=(150, 160, 200, alpha),
            outline=(180, 190, 220, alpha),
        )


def draw_sparkles(draw, cx, cy, frame, total):
    """Draw sparkle effects around the spider."""
    phase = (frame % total) / total
    sparkle_positions = [
        (cx - 60, cy - 50, 0),
        (cx + 55, cy - 45, 0.25),
        (cx - 40, cy + 30, 0.5),
        (cx + 50, cy + 25, 0.75),
        (cx, cy - 65, 0.125),
    ]
    for sx, sy, offset in sparkle_positions:
        progress = (phase + offset) % 1.0
        size = 3 + 4 * abs(math.sin(progress * math.pi))
        alpha = int(200 * abs(math.sin(progress * math.pi)))
        # 4-point star
        draw.line([(sx - size, sy), (sx + size, sy)],
                  fill=(255, 220, 100, alpha), width=2)
        draw.line([(sx, sy - size), (sx, sy + size)],
                  fill=(255, 220, 100, alpha), width=2)


def make_idle_gif(base_img, size, out_path):
    """Idle: breathing scale + subtle eye blink."""
    frames = []
    n = 20
    for i in range(n):
        t = i / n
        # Breathing: scale 0.97 ~ 1.03
        scale = 1.0 + 0.03 * math.sin(t * 2 * math.pi)
        w, h = base_img.size
        new_w, new_h = int(w * scale), int(h * scale)
        scaled = base_img.resize((new_w, new_h), Image.Resampling.LANCZOS)

        canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        x = (size - new_w) // 2
        y = (size - new_h) // 2 + int(2 * math.sin(t * 2 * math.pi))
        canvas.paste(scaled, (x, y), scaled)

        # Blink: frames 17-19 have narrower eyes
        if i >= 17:
            draw = ImageDraw.Draw(canvas)
            # Find approximate eye positions and draw over with half-height
            # Since it's pixel art, we add a subtle overlay
            pass

        frames.append(canvas)

    frames[0].save(
        out_path, save_all=True, append_images=frames[1:],
        duration=100, loop=0, disposal=2, transparency=0,
    )
    print(f"  -> {out_path} ({n} frames)")


def make_crawling_gif(base_img, size, out_path):
    """Crawling: slight side-to-side wobble + vertical bounce."""
    frames = []
    n = 12
    for i in range(n):
        t = i / n
        # Wobble
        dx = int(3 * math.sin(t * 2 * math.pi))
        dy = int(2 * abs(math.sin(t * 2 * math.pi)))
        # Slight scale pulse
        scale = 1.0 + 0.02 * math.sin(t * 4 * math.pi)
        w, h = base_img.size
        new_w, new_h = int(w * scale), int(h * scale)
        scaled = base_img.resize((new_w, new_h), Image.Resampling.LANCZOS)

        canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        x = (size - new_w) // 2 + dx
        y = (size - new_h) // 2 - dy
        canvas.paste(scaled, (x, y), scaled)
        frames.append(canvas)

    frames[0].save(
        out_path, save_all=True, append_images=frames[1:],
        duration=80, loop=0, disposal=2, transparency=0,
    )
    print(f"  -> {out_path} ({n} frames)")


def make_thinking_gif(base_img, size, out_path):
    """Thinking: thought bubbles + subtle sway."""
    frames = []
    n = 16
    # Find spider top for bubble placement
    bbox = base_img.getbbox()
    top_y = bbox[1] if bbox else 30
    cx = size // 2

    for i in range(n):
        t = i / n
        dx = int(2 * math.sin(t * 2 * math.pi))
        w, h = base_img.size

        canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        x = (size - w) // 2 + dx
        y = (size - h) // 2
        canvas.paste(base_img, (x, y), base_img)

        draw = ImageDraw.Draw(canvas)
        draw_thought_bubbles(draw, cx + 20, top_y, i, n)
        frames.append(canvas)

    frames[0].save(
        out_path, save_all=True, append_images=frames[1:],
        duration=120, loop=0, disposal=2, transparency=0,
    )
    print(f"  -> {out_path} ({n} frames)")


def make_happy_gif(base_img, size, out_path):
    """Happy: bounce + sparkles."""
    frames = []
    n = 16
    for i in range(n):
        t = i / n
        # Bounce
        bounce = int(6 * abs(math.sin(t * 2 * math.pi)))
        # Squash and stretch
        sy = 1.0 + 0.05 * math.sin(t * 2 * math.pi)
        sx = 1.0 - 0.03 * math.sin(t * 2 * math.pi)
        w, h = base_img.size
        new_w, new_h = int(w * sx), int(h * sy)
        scaled = base_img.resize((new_w, new_h), Image.Resampling.LANCZOS)

        canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        x = (size - new_w) // 2
        y = (size - new_h) // 2 - bounce
        canvas.paste(scaled, (x, y), scaled)

        draw = ImageDraw.Draw(canvas)
        draw_sparkles(draw, size // 2, size // 2, i, n)
        frames.append(canvas)

    frames[0].save(
        out_path, save_all=True, append_images=frames[1:],
        duration=80, loop=0, disposal=2, transparency=0,
    )
    print(f"  -> {out_path} ({n} frames)")


def main():
    print("Loading source image...")
    src = Image.open(SOURCE)
    src = remove_background(src)
    src = crop_to_content(src)
    base = fit_to_size(src, TARGET_SIZE)

    # Save transparent base for reference
    base.save(ASSETS_DIR / "spider_base.png")
    print(f"  -> spider_base.png (transparent base, {base.size})")

    print("Generating GIFs...")
    make_idle_gif(base, TARGET_SIZE, ASSETS_DIR / "spider_idle.gif")
    make_crawling_gif(base, TARGET_SIZE, ASSETS_DIR / "spider_crawling.gif")
    make_thinking_gif(base, TARGET_SIZE, ASSETS_DIR / "spider_thinking.gif")
    make_happy_gif(base, TARGET_SIZE, ASSETS_DIR / "spider_happy.gif")

def make_wave_gif(base_img, size, out_path):
    """Wave: tilt left-right like greeting."""
    frames = []
    n = 16
    for i in range(n):
        t = i / n
        # Tilt angle: -15 to +15 degrees
        angle = 15 * math.sin(t * 2 * math.pi)
        rotated = base_img.rotate(angle, resample=Image.Resampling.BICUBIC, expand=False)
        canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        w, h = rotated.size
        x = (size - w) // 2
        y = (size - h) // 2
        canvas.paste(rotated, (x, y), rotated)
        frames.append(canvas)

    frames[0].save(
        out_path, save_all=True, append_images=frames[1:],
        duration=60, loop=0, disposal=2, transparency=0,
    )
    print(f"  -> {out_path} ({n} frames)")


def make_jump_gif(base_img, size, out_path):
    """Jump: bounce up high with squash-stretch."""
    frames = []
    n = 16
    for i in range(n):
        t = i / n
        # Jump arc: up then down
        bounce = int(20 * math.sin(t * math.pi))
        sy = 1.0 + 0.08 * math.sin(t * math.pi)
        sx = 1.0 - 0.05 * math.sin(t * math.pi)
        w, h = base_img.size
        new_w, new_h = int(w * sx), int(h * sy)
        scaled = base_img.resize((new_w, new_h), Image.Resampling.LANCZOS)
        canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        x = (size - new_w) // 2
        y = (size - new_h) // 2 - bounce
        canvas.paste(scaled, (x, y), scaled)

        # Impact lines at peak
        if 6 <= i <= 10:
            draw = ImageDraw.Draw(canvas)
            cx, cy = size // 2, size // 2 + 10
            for angle_deg in [0, 45, 90, 135]:
                rad = math.radians(angle_deg)
                r1, r2 = 45, 55
                draw.line(
                    [(cx + r1 * math.cos(rad), cy + r1 * math.sin(rad)),
                     (cx + r2 * math.cos(rad), cy + r2 * math.sin(rad))],
                    fill=(200, 200, 200, 150), width=2
                )

        frames.append(canvas)

    frames[0].save(
        out_path, save_all=True, append_images=frames[1:],
        duration=60, loop=0, disposal=2, transparency=0,
    )
    print(f"  -> {out_path} ({n} frames)")


def make_spin_gif(base_img, size, out_path):
    """Spin: rotate 360 degrees."""
    frames = []
    n = 20
    for i in range(n):
        angle = 360 * (i / n)
        rotated = base_img.rotate(-angle, resample=Image.Resampling.BICUBIC, expand=False)
        canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        w, h = rotated.size
        x = (size - w) // 2
        y = (size - h) // 2
        canvas.paste(rotated, (x, y), rotated)
        frames.append(canvas)

    frames[0].save(
        out_path, save_all=True, append_images=frames[1:],
        duration=50, loop=0, disposal=2, transparency=0,
    )
    print(f"  -> {out_path} ({n} frames)")


def make_nod_gif(base_img, size, out_path):
    """Nod: tilt down then back up."""
    frames = []
    n = 12
    for i in range(n):
        t = i / n
        # Nod: 0 -> -12 -> 0
        angle = -12 * math.sin(t * math.pi)
        # Slight forward lean
        dy = int(3 * math.sin(t * math.pi))
        rotated = base_img.rotate(angle, resample=Image.Resampling.BICUBIC, expand=False)
        canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        w, h = rotated.size
        x = (size - w) // 2
        y = (size - h) // 2 + dy
        canvas.paste(rotated, (x, y), rotated)
        frames.append(canvas)

    frames[0].save(
        out_path, save_all=True, append_images=frames[1:],
        duration=80, loop=0, disposal=2, transparency=0,
    )
    print(f"  -> {out_path} ({n} frames)")


def main():
    print("Loading source image...")
    src = Image.open(SOURCE)
    src = remove_background(src)
    src = crop_to_content(src)
    base = fit_to_size(src, TARGET_SIZE)

    # Save transparent base for reference
    base.save(ASSETS_DIR / "spider_base.png")
    print(f"  -> spider_base.png (transparent base, {base.size})")

    print("Generating state GIFs...")
    make_idle_gif(base, TARGET_SIZE, ASSETS_DIR / "spider_idle.gif")
    make_crawling_gif(base, TARGET_SIZE, ASSETS_DIR / "spider_crawling.gif")
    make_thinking_gif(base, TARGET_SIZE, ASSETS_DIR / "spider_thinking.gif")
    make_happy_gif(base, TARGET_SIZE, ASSETS_DIR / "spider_happy.gif")

    print("Generating interaction GIFs...")
    make_wave_gif(base, TARGET_SIZE, ASSETS_DIR / "spider_wave.gif")
    make_jump_gif(base, TARGET_SIZE, ASSETS_DIR / "spider_jump.gif")
    make_spin_gif(base, TARGET_SIZE, ASSETS_DIR / "spider_spin.gif")
    make_nod_gif(base, TARGET_SIZE, ASSETS_DIR / "spider_nod.gif")

    print("Done!")


if __name__ == "__main__":
    main()
