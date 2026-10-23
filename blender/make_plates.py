# Number plate textures in the pre-1945 German style (white enamel, black edge, narrow DIN-like
# figures), after the Munich motorcycle pair IIA-83356 in the Deutsches Museum Verkehrszentrum and
# Bundesarchiv Bild 183-H08684 (Berlin 1938). The registration is made up.
#   python3 make_plates.py <textures_dir>
# Front: a curved strip on the mudguard; the texture is the strip laid straight (u along the arc,
# v across it), build_r12.py bends it. Rear: two lines with clipped top corners.
import sys, os
from PIL import Image, ImageDraw, ImageFont

OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), 'textures')
REG = ('IIA', '36812')       # II = Bavaria, A = Upper Bavaria / Munich
WHITE = (236, 233, 222)
BLACK = (20, 20, 20)
FONT = '/System/Library/Fonts/Supplemental/DIN Alternate Bold.ttf'

# keep in step with build_r12.py
FRONT_LEN, FRONT_H, FRONT_R = 0.3100, 0.07, 0.011
REAR_W, REAR_H, REAR_CH = 0.19, 0.125, 0.034

def glyphs(text, cap_px, squeeze=0.86, track=0.08):
    """Render text with the figures narrowed like the plate lettering; returns an L image (ink=255)."""
    f = ImageFont.truetype(FONT, int(cap_px / 0.7))
    tiles = []
    for ch in text:
        im = Image.new('L', (int(cap_px * 2), int(cap_px * 2)), 0)
        ImageDraw.Draw(im).text((cap_px * 0.2, cap_px * 0.1), ch, font=f, fill=255)
        bb = im.getbbox()
        g = im.crop(bb)
        if ch == '-':
            # the dash sits at mid height with the figures' stroke weight
            g = Image.new('L', (int(cap_px * 0.34), int(cap_px * 0.13)), 255)
        else:
            g = g.resize((max(1, int(g.width * squeeze)), int(cap_px)), Image.LANCZOS)
        tiles.append((ch, g))
    gap = int(cap_px * track)
    width = sum(g.width for _, g in tiles) + gap * (len(tiles) - 1)
    out = Image.new('L', (width, int(cap_px)), 0)
    x = 0
    for ch, g in tiles:
        y = (out.height - g.height) // 2
        out.paste(g, (x, y))
        x += g.width + gap
    return out

def ink(img, mask, x, y):
    img.paste(Image.new('RGB', mask.size, BLACK), (x, y), mask)

# ---------------------------------------------------------------- front strip
W = 2048
H = round(W * FRONT_H / FRONT_LEN)
ppm = W / FRONT_LEN
im = Image.new('RGB', (W, H), BLACK)
d = ImageDraw.Draw(im)
edge = round(0.0045 * ppm)
d.rounded_rectangle([edge, edge, W - 1 - edge, H - 1 - edge], radius=round((FRONT_R - 0.0045) * ppm), fill=WHITE)
# the figures run nearly end to end on the originals: open the spacing until they fill the strip
avail = W - 2 * round(0.017 * ppm)
track = 0.06
while True:
    t = glyphs(REG[0] + '-' + REG[1], cap_px=H * 0.66, squeeze=0.95, track=track)
    if t.width >= avail * 0.95 or track > 0.24:
        break
    track += 0.01
if t.width > avail:
    t = t.resize((avail, t.height), Image.LANCZOS)
ink(im, t, (W - t.width) // 2, (H - t.height) // 2)
im.save(os.path.join(OUT, 'plate_front.png'))

# ---------------------------------------------------------------- rear plate
W = 1024
H = round(W * REAR_H / REAR_W)
ppm = W / REAR_W
ch = REAR_CH * ppm
def outline(inset):
    i = inset
    c = ch - inset * 0.414
    return [(i, H - 1 - i), (W - 1 - i, H - 1 - i), (W - 1 - i, c + i), (W - 1 - c - i, i), (c + i, i), (i, c + i)]
im = Image.new('RGB', (W, H), BLACK)
d = ImageDraw.Draw(im)
d.polygon(outline(round(0.004 * ppm)), fill=WHITE)
top = glyphs(REG[0], cap_px=H * 0.3, track=0.14)
bot = glyphs(REG[1], cap_px=H * 0.36, track=0.1)
avail = W - 2 * round(0.012 * ppm)
if bot.width > avail:
    bot = bot.resize((avail, bot.height), Image.LANCZOS)
ink(im, top, (W - top.width) // 2, round(H * 0.13))
ink(im, bot, (W - bot.width) // 2, round(H * 0.53))
im.save(os.path.join(OUT, 'plate_rear.png'))
print('plates', REG)
