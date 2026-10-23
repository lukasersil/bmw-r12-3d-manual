# Cut the period sources for the part cards into web images.
#   python3 tools/make_media.py <handbook page images> <downloaded photos> <out: media/>
# Handbook pages come from `pdfimages -j bmw_r12-r17_owners_handbook_1935-1942.pdf pg`, photos from
# Wikimedia Commons (files and credits in media_spec.py). Writes media/<id>.jpg and media/t/<id>.jpg.
import os, sys
from PIL import Image, ImageFilter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from media_spec import FIGS, PHOTOS

HB, PH, OUT = sys.argv[1:4]
os.makedirs(os.path.join(OUT, 't'), exist_ok=True)
total = 0

def save(im, name, big):
    global total
    im = im.convert('RGB')
    full = im.copy()
    full.thumbnail((big, big), Image.LANCZOS)
    if full.width < im.width:
        full = full.filter(ImageFilter.UnsharpMask(radius=0.8, percent=40, threshold=2))
    p = os.path.join(OUT, name + '.jpg')
    full.save(p, quality=82, optimize=True, progressive=True)
    th = im.copy()
    th.thumbnail((360, 240), Image.LANCZOS)
    q = os.path.join(OUT, 't', name + '.jpg')
    th.save(q, quality=78, optimize=True)
    total += os.path.getsize(p) + os.path.getsize(q)
    print(name, full.size, os.path.getsize(p) // 1024, 'kB')

for k, (pg, box, *_rest) in FIGS.items():
    save(Image.open(os.path.join(HB, pg + '.jpg')).crop(box), k, 1600 if k == 'f01' else 1100)
for k, (f, box, _cr) in PHOTOS.items():
    im = Image.open(os.path.join(PH, f))
    save(im.crop(box) if box else im, k, 1400)
print('TOTAL', total // 1024, 'kB')
