"""YouTube cover (1920x1080) for 'Democratic Kampuchea 1975-1979: We Remember' in the film's memory-drawing look:
Yeay Sophal and Malis light incense at the memorial (warm colour, left) as it dissolves into the grey pencil memory of
the road out of the city (right); the title is hand-lettered on an aged notebook page, the years in candle orange.
Writes film/cover_democratic_kampuchea.png / .jpg (and a 1280x720 jpg under 2 MB)."""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "engine"))
sys.path.insert(0, ROOT)
os.chdir(ROOT)

import cairocffi as cairo  # noqa: E402
import numpy as np  # noqa: E402

import film  # noqa: E402
import memory as MEM  # noqa: E402
import sets75 as T  # noqa: E402
from core import H, W, surface, surface_to_np, np_to_surface, text_surface, value_noise  # noqa: E402
from sets import F, grp  # noqa: E402


def render(scene, cam, color, dark=0.0):
    s = surface(W, H)
    c = cairo.Context(s)
    c.set_source_rgb(0, 0, 0)
    c.paint()
    film.draw_scene_ink(c, s, scene, 3.0, 8.0, dict(a=cam, b=cam), "full", dark, color)
    s.flush()
    return surface_to_np(s).astype(np.float32) / 255.0


# present: the two of them at the incense pot (warm colour)
present = render(T.make_memorial("morning", people=[grp(0.9, F(1420, 1250, 430, "sophal_old", "kneel_pray", 60, 11,
                                                                  expr="calm"),
                                                         F(1250, 1262, 420, "malis", "pray", 40, 12, expr="calm"))]),
                 (1780, 990, 1.62), 1.0)
# memory: the road out of the city, April 1975 (grey pencil)
memory = render(T.make_exodus("grey", people=[grp(0.6, *T.crowd(22, 7, x0=600, x1=1900))]), (1250, 1000, 1.3), 0.0, 0.05)

# dissolve from present (left) into memory (right) along a soft, smoky edge
n = value_noise(W // 2, H // 2, 4, 1975, 5)
n = (n - n.min()) / (n.max() - n.min())
n = np.kron(n, np.ones((2, 2), np.float32))[:H, :W]
xx = np.tile(np.linspace(0, 1, W, dtype=np.float32), (H, 1))
a = np.clip((xx - 0.30) / 0.14 + (n - 0.5) * 0.9, 0, 1)[..., None]
img = present * (1 - a) + memory * a
img[..., 3] = 1.0
s = np_to_surface(img[..., [2, 1, 0, 3]])   # BGRA (cairo) -> RGBA
c = cairo.Context(s)

# aged notebook page with the title (right)
PX, PY, PW, PH = 1150, 70, 720, 940
page = surface(PW, PH)
pc = cairo.Context(page)
pc.scale(PW / W, PH / H)
MEM.paper(pc, MEM.PAPER, 1979, lines=False, margin=False)
c.save()
c.translate(PX + PW / 2, PY + PH / 2)
c.rotate(0.012)
c.translate(-PW / 2, -PH / 2)
c.set_source_rgba(0, 0, 0, 0.5)
c.rectangle(14, 18, PW, PH)
c.fill()
c.set_source_surface(page, 0, 0)
c.paint()
for k in range(18):   # faint ruled lines
    c.set_source_rgba(0.5, 0.56, 0.65, 0.16)
    c.rectangle(0, 110 + k * 46, PW, 1.6)
    c.fill()
c.set_source_rgba(0.69, 0.32, 0.29, 0.22)
c.rectangle(70, 0, 2, PH)
c.fill()


def centred(txt, size, col, font, weight, y, width=660, alpha=1.0):
    t = text_surface(txt, size, col, font, weight, width=width, align="center")
    c.set_source_surface(t, (PW - t.get_width()) / 2, y)
    c.paint_with_alpha(alpha)
    return t.get_height()


y = 36
y += centred("ភាពយន្តឯកសារ ប្រវត្តិសាស្ត្រ", 28, "#5a554c", "Battambang", "", y)
y += 6
y += centred("កម្ពុជា", 100, MEM.GRAPHITE, "Koulen", "", y) - 34
y += centred("ប្រជាធិបតេយ្យ", 86, MEM.GRAPHITE, "Koulen", "", y) - 8
y += centred("DEMOCRATIC KAMPUCHEA", 46, MEM.GRAPHITE, "Futura", "Bold", y) + 16
# the years on a charcoal band, in candle orange
c.set_source_rgb(0.12, 0.115, 0.105)
yrs = text_surface("១៩៧៥ – ១៩៧៩", 76, "#e8a04a", "Koulen", "", width=660, align="center")
band = 14 + yrs.get_height() - 18 + 46
c.rectangle(40, y, PW - 80, band)
c.fill()
yy = y + 14
yy += centred("១៩៧៥ – ១៩៧៩", 76, "#e8a04a", "Koulen", "", yy) - 18
centred("17 APRIL 1975 – 6 JANUARY 1979", 28, "#efe7d2", "Futura", "Medium", yy)
y += band + 18
y += centred("យើងចងចាំ · We Remember", 46, "#3a3630", "Battambang", "Bold", y) + 8
MEM.pencil_underline(c, PW / 2 - 200, y, 400, 1.0, seed=4, a=0.55)
y += 22
centred("HISTORY DOCUMENTARY · 15 MIN · KHMER, ENGLISH SUBTITLES", 18, "#4a463e", "Futura", "Medium", y)
c.restore()

# a small candle on the low table in the warm half
MEM.candle(c, 330, 1040, 1.6, 0.4)

out = os.path.join(ROOT, "film", "cover_democratic_kampuchea")
s.write_to_png(out + ".png")
from PIL import Image  # noqa: E402
im = Image.open(out + ".png").convert("RGB")
im.save(out + ".jpg", quality=92)
im.resize((1280, 720), Image.LANCZOS).save(out + "_1280.jpg", quality=88)
print(out + ".png")
