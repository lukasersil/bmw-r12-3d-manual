# Fluted headlamp lens of the period Bosch lamp: fine vertical prism flutes over the whole glass,
# broken into staggered horizontal rows, with the silvered reflector showing bright through it
# (museum photo of a 1936 R 12, media/p_1936.jpg).
#   python3 tools/make_lens.py blender/textures/lens.png
import sys
import numpy as np
from PIL import Image

N = 512
FLUTES = 44          # flutes across the diameter
ROWS = 5             # rows of prism segments, every other row offset by half a flute

y, x = np.mgrid[0:N, 0:N].astype(np.float32)
u = (x + 0.5) / N * 2 - 1
v = 1 - (y + 0.5) / N * 2
r = np.sqrt(u * u + v * v)

row = np.floor((v + 1) / 2 * ROWS)
shift = (row % 2) * 0.5
f = (u + 1) / 2 * FLUTES + shift
t = f - np.floor(f)                      # position across one flute, 0..1
# a cylindrical flute: light on one flank, shade on the other, thin dark groove between flutes
flank = np.cos(t * np.pi)                # +1 at the left edge, -1 at the right
lum = 0.88 + 0.1 * flank
lum -= 0.13 * np.exp(-((t - 0.0) / 0.05) ** 2) + 0.13 * np.exp(-((t - 1.0) / 0.05) ** 2)
# row breaks: a faint horizontal step where the prism rows meet
rv = (v + 1) / 2 * ROWS
rb = rv - np.floor(rv)
lum -= 0.045 * np.exp(-((rb - 0.0) / 0.02) ** 2) + 0.045 * np.exp(-((rb - 1.0) / 0.02) ** 2)
# reflector: bright towards the centre, darker near the rim where the shell shades it
lum *= 0.86 + 0.2 * np.exp(-(r / 0.55) ** 2)
lum *= 1 - 0.14 * np.clip((r - 0.78) / 0.22, 0, 1)
# slight unevenness between flutes, as the pressed glass has
rng = np.random.default_rng(12)
jit = rng.normal(0, 0.03, (ROWS + 1, FLUTES + 2)).astype(np.float32)
lum += jit[row.astype(int).clip(0, ROWS), np.floor(f).astype(int).clip(0, FLUTES + 1)]
lum = np.clip(lum, 0, 1)

rgb = np.stack([lum * 0.95, lum * 0.97, lum * 1.0], -1)
alpha = np.where(r <= 1.0, 0.93, 0.0)
img = np.concatenate([rgb, alpha[..., None]], -1)
Image.fromarray((img * 255).round().astype(np.uint8), 'RGBA').save(sys.argv[1])
print('wrote', sys.argv[1], N, 'px')
