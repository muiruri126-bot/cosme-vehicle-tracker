"""
Generate app icons in multiple sizes for organization library upload.
Uses cairosvg + Pillow to convert the SVG icon to PNG at various standard sizes.

Install deps:  pip install cairosvg Pillow

Run:  python generate_icons.py
"""

import os
import sys

try:
    import cairosvg
except ImportError:
    print("cairosvg not found, trying alternative method...")
    cairosvg = None

try:
    from PIL import Image
except ImportError:
    print("Pillow not found. Install with: pip install Pillow")
    sys.exit(1)

# Standard icon sizes for various platforms
ICON_SIZES = {
    "favicon-16x16.png": 16,
    "favicon-32x32.png": 32,
    "apple-touch-icon.png": 180,
    "icon-48x48.png": 48,
    "icon-72x72.png": 72,
    "icon-96x96.png": 96,
    "icon-128x128.png": 128,
    "icon-144x144.png": 144,
    "icon-152x152.png": 152,
    "icon-192x192.png": 192,
    "icon-256x256.png": 256,
    "icon-384x384.png": 384,
    "icon-512x512.png": 512,
}

# ICO file for browser favicon
ICO_SIZES = [16, 32, 48]

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SVG_PATH = os.path.join(SCRIPT_DIR, "static", "app-icon.svg")
ICONS_DIR = os.path.join(SCRIPT_DIR, "static", "icons")


def generate_with_cairosvg():
    """Generate PNG icons using cairosvg (best quality)."""
    os.makedirs(ICONS_DIR, exist_ok=True)

    for filename, size in ICON_SIZES.items():
        output_path = os.path.join(ICONS_DIR, filename)
        cairosvg.svg2png(
            url=SVG_PATH,
            write_to=output_path,
            output_width=size,
            output_height=size,
        )
        print(f"  Created {filename} ({size}x{size})")

    # Generate .ico file
    ico_images = []
    for size in ICO_SIZES:
        png_data = cairosvg.svg2png(
            url=SVG_PATH,
            output_width=size,
            output_height=size,
        )
        from io import BytesIO
        img = Image.open(BytesIO(png_data))
        ico_images.append(img)

    ico_path = os.path.join(ICONS_DIR, "favicon.ico")
    ico_images[0].save(
        ico_path,
        format="ICO",
        sizes=[(s, s) for s in ICO_SIZES],
        append_images=ico_images[1:],
    )
    print(f"  Created favicon.ico ({', '.join(f'{s}x{s}' for s in ICO_SIZES)})")


def generate_with_pillow_fallback():
    """Fallback: Generate icons from the largest PNG using Pillow resize.
    This requires at least one pre-existing PNG or uses a programmatic icon.
    """
    os.makedirs(ICONS_DIR, exist_ok=True)

    # Create a programmatic icon using Pillow
    from PIL import ImageDraw, ImageFont

    size = 512
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Rounded rectangle background
    radius = 96
    # Draw background with gradient approximation
    for y in range(size):
        ratio = y / size
        r = int(0 + (0 * ratio))
        g = int(78 + (116 - 78) * ratio)
        b = int(154 + (228 - 154) * ratio)
        draw.line([(0, y), (size - 1, y)], fill=(r, g, b, 255))

    # Apply rounded corners by masking
    mask = Image.new("L", (size, size), 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.rounded_rectangle([(0, 0), (size - 1, size - 1)], radius=radius, fill=255)
    img.putalpha(mask)

    # Draw vehicle body (simplified)
    cx, cy = 256, 240
    # Body
    draw.rounded_rectangle(
        [(cx - 110, cy - 15), (cx + 110, cy + 40)],
        radius=10,
        fill=(255, 255, 255, 230),
    )
    # Cabin
    draw.polygon(
        [(cx - 60, cy - 60), (cx - 40, cy - 15), (cx + 70, cy - 15), (cx + 50, cy - 60)],
        fill=(255, 255, 255, 200),
        outline=(224, 224, 224),
    )
    # Wheels
    for wx in [cx - 60, cx + 65]:
        draw.ellipse([(wx - 22, cy + 38), (wx + 22, cy + 82)], fill=(55, 71, 79))
        draw.ellipse([(wx - 14, cy + 46), (wx + 14, cy + 74)], fill=(120, 144, 156))
        draw.ellipse([(wx - 6, cy + 54), (wx + 6, cy + 66)], fill=(55, 71, 79))

    # GPS pin
    px, py = 350, 120
    draw.polygon(
        [(px, py + 55), (px - 35, py - 5), (px - 30, py - 35), (px + 30, py - 35), (px + 35, py - 5)],
        fill=(255, 255, 255, 240),
    )
    draw.ellipse([(px - 35, py - 45), (px + 35, py + 15)], fill=(255, 255, 255, 240))
    draw.ellipse([(px - 15, py - 20), (px + 15, py + 10)], fill=(0, 105, 217))
    draw.ellipse([(px - 6, py - 11), (px + 6, py + 1)], fill=(255, 255, 255))

    # Text
    try:
        font = ImageFont.truetype("arial.ttf", 36)
    except (IOError, OSError):
        font = ImageFont.load_default()

    text = "VRT"
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    draw.text(((size - tw) // 2, 430), text, fill=(255, 255, 255, 220), font=font)

    # Save all sizes
    for filename, s in ICON_SIZES.items():
        resized = img.resize((s, s), Image.LANCZOS)
        output_path = os.path.join(ICONS_DIR, filename)
        resized.save(output_path, "PNG")
        print(f"  Created {filename} ({s}x{s})")

    # Generate .ico
    ico_images = [img.resize((s, s), Image.LANCZOS) for s in ICO_SIZES]
    ico_path = os.path.join(ICONS_DIR, "favicon.ico")
    ico_images[0].save(
        ico_path,
        format="ICO",
        sizes=[(s, s) for s in ICO_SIZES],
        append_images=ico_images[1:],
    )
    print(f"  Created favicon.ico ({', '.join(f'{s}x{s}' for s in ICO_SIZES)})")

    return img


def main():
    print("=" * 50)
    print("Vehicle Request Tracker – Icon Generator")
    print("=" * 50)
    print()

    if cairosvg:
        print("Using cairosvg (SVG → PNG, best quality)...")
        generate_with_cairosvg()
    else:
        print("Using Pillow fallback (programmatic icon)...")
        generate_with_pillow_fallback()

    print()
    print(f"Icons saved to: {ICONS_DIR}")
    print()
    print("Files ready for upload:")
    for f in sorted(os.listdir(ICONS_DIR)):
        fpath = os.path.join(ICONS_DIR, f)
        fsize = os.path.getsize(fpath)
        print(f"  {f:30s}  {fsize:>8,} bytes")


if __name__ == "__main__":
    main()
