"""Production documents for 'Democratic Kampuchea 1975-1979: We Remember', written from the live shot list:
docs/script_km_en.md, docs/storyboard.md, docs/shot_list.md, docs/on_screen_text.md, docs/archive_and_licences.md."""
import inspect
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "engine"))
sys.path.insert(0, ROOT)
os.chdir(ROOT)
import script_src as SS  # noqa: E402
from narration import N, WHO, SRC, VOICES  # noqa: E402

shots, pl, cues = SS.build()
total = shots[-1]["start"] + shots[-1]["dur"]
PROJ = json.load(open("project.json"))


def tc(t):
    return "%d:%02d" % (t // 60, t % 60)


src_all = open("script_src.py").read()
CHS = [(int(m.group(1)), m.group(2), m.group(3), m.group(4))
       for m in re.finditer(r'CH\((\d+), "([^"]+)", "([^"]+)", "([^"]+)"', src_all)]
CHS = [(n, km, en.replace("\\u201c", "“").replace("\\u201d", "”"), y) for (n, km, en, y) in CHS]
NAMES = [("0", "បើក", "Opening", "")] + [(str(n), km, en, y) for (n, km, en, y) in CHS] + [("—", "បញ្ចប់", "Closing", "")]


def chap(i):
    k = 0
    for j, b in enumerate(SS.CHAPTERS):
        if i >= b:
            k = j + 1
    return NAMES[min(k, len(NAMES) - 1)]


SETS = {
    "make_memorial": "Present day, warm colour: a memorial stupa at dawn (tiered roofs, naga finials), frangipani trees, "
                     "a lotus pond, an incense pot with smoke curling up",
    "make_altar": "Present day: a low altar table with a pencil portrait of Sophal's father (fictional), lotus, incense "
                  "and a white candle",
    "make_exodus": "Memory, grey pencil: a national road leaving Phnom Penh; sugar palms; an abandoned car and cart; "
                   "dust drifting (1979: the same road, empty and overgrown)",
    "make_still": "Memory, close-up symbol on paper",
    "make_classroom": "Memory/symbol: a classroom with windows and shafts of light",
    "make_fields": "Memory: cooperative paddy re-dug into straight squares; sugar palms on the horizon",
    "make_hall": "Memory: a communal dining hall under a thatched roof; long tables and tin bowls",
    "make_newsstand": "Memory: a Phnom Penh shophouse street (shutters, balconies, a kiosk, a lamp post)",
    "make_empty": "Memory: the same street, empty, papers blowing along it",
    "make_village": "Memory: a village of stilt houses and paddy dykes",
    "make_palace60": "Memory: the palace roofs by the river",
    "make_assembly": "Reconstruction: the assembly hall, rows of seated deputies",
    "make_border": "Reconstruction: the border at night, tree-line and distant flashes (schematic)",
    "album_photo": "Authentic image mounted as an old print in a family album (photo corners, pencil caption)",
    "memorial_frame": "Authentic photo in a wooden frame on a memorial table, a candle beside it",
    "map_scene": "Animated paper-relief map (real relief and rivers), schematic routes/labels drawn on",
    "pencil_chapter": "Hand-written pencil chapter title on a ruled notebook page, the chapter's sketch showing through",
    "title_card": "Title written over the memorial at dawn",
    "text_page": "Quiet text on dark paper",
    "sources_differ": "Notebook page: a hand-ruled table of what the sources say",
    "scrolling_credits": "Scrolling credits",
}
STILLS = {"shoes": "a pair of sandals left on the road", "glasses": "a teacher's broken spectacles on a closed book",
          "bowl": "a tin bowl of thin porridge and a spoon", "notes": "riel banknotes blowing across the ground",
          "books": "books on a classroom floor", "gate": "a pagoda gate, chained shut, weeds at its foot",
          "krama": "a blue krama on a bamboo fence"}


def vis_src(i):
    try:
        return inspect.getsource(SS.SHOTS[i]["vis"]).strip()
    except Exception:
        return ""


def setting(i):
    s = vis_src(i)
    out = []
    for k, v in SETS.items():
        if k + "(" in s or ("AP(" in s and k == "album_photo") or ("MF(" in s and k == "memorial_frame"):
            out.append(v)
            break
    m = re.search(r'make_still\("(\w+)"', s)
    if m:
        out.append(STILLS.get(m.group(1), ""))
    m = re.search(r'make_classroom\("(\w+)"', s)
    if m:
        out.append("abandoned classroom, books on the floor" if m.group(1) == "books" else
                   "a barred, empty room with a single chair (S-21 as symbol: nothing else is shown)")
    m = re.search(r'_path\(f\)|AP\("([^"]+)"', s)
    if not out and shots[i].get("badge") == "guide":
        out.append(SETS["make_altar"] if "m10" in shots[i]["lines"] else SETS["make_memorial"] +
                   "; close on Malis and Yeay Sophal by the incense pot, mouths lip-synced to the voice")
    return "; ".join(x for x in out if x) or "—"


def people(i):
    s = vis_src(i)
    found = sorted(set(re.findall(r'"(sophal_old|malis|sophal_y|sophal_k|mom75|dad75|vuthy|vuthy_k|kr_soldier|'
                                  r'worker_m|worker_w|child_k|blue_m|blue_w|mourner_m|mourner_w|kh_monk)"', s)))
    if "sophal(" in s or (shots[i].get("badge") == "guide" and "m10" not in shots[i]["lines"]):
        found.append("sophal_old")
    if "malis(" in s or shots[i].get("badge") == "guide":
        found.append("malis")
    if "pair(" in s:
        found += ["sophal_old", "malis"]
    if "crowd(" in s:
        found.append("crowd of evacuees")
    if "workers(" in s:
        found.append("cooperative workers in black")
    if "FAMILY(" in s:
        found.append("Sophal's family (1975)")
    return ", ".join(sorted(set(found))) or "—"


def camtxt(c):
    a, b = c.get("a"), c.get("b")
    if not a:
        return "static"
    za, zb = a[2], b[2]
    mv = "push in" if zb > za * 1.02 else ("pull out" if zb < za * 0.98 else "hold")
    pan = ""
    if abs(b[0] - a[0]) > 40:
        pan = ", pan " + ("right" if b[0] > a[0] else "left")
    if abs(b[1] - a[1]) > 40:
        pan += ", tilt " + ("down" if b[1] > a[1] else "up")
    return "%s (zoom %.2f→%.2f)%s" % (mv, za, zb, pan)


TRANS = {"smoke": "incense smoke drifts across", "page": "notebook / album page turns", "redraw":
         "pencil lines fade and redraw", None: "soft dissolve", "fade": "soft dissolve"}

# ---------------------------------------------------------------- script
md = ["# %s · %s" % (PROJ["title_km"], PROJ["title_en"]), "",
      "## Narration and dialogue script (Khmer / English), timed", "",
      "Runtime %s. Voices: Narrator (adult man) · **YEAY SOPHAL** (fictional elderly survivor) · **MALIS** (fictional "
      "granddaughter, 15). Every factual narrator line carries its source code from `docs/research_brief.md`. "
      "Sophal's and Malis's lines are fiction (a composite family story)." % tc(total), ""]
cur = None
for p in pl:
    i = [k for k, s in enumerate(shots) if s["start"] <= p["t"] < s["start"] + s["dur"]]
    ch = chap(i[-1] if i else 0)
    if ch != cur:
        cur = ch
        md += ["", "### %s · %s %s" % (ch[1], ch[2], ("(" + ch[3] + ")") if ch[3] else ""), ""]
    who = VOICES.get(p["who"], {}).get("label_en", "").strip(" :") or "NARRATOR"
    km, en = N[p["key"]]
    md += ["**%s · %s** · `%s`%s" % (tc(p["t"]), who, p["key"],
                                    (" · _source: %s_" % SRC[p["key"]]) if SRC.get(p["key"]) and p["who"] == "nar" else ""),
           "", km, "", "> " + en, ""]
words = sum(len(N[k][1].split()) for k in N)
md += ["", "---", "English words: %d (narration %d, guides %d)." % (
    words, sum(len(N[k][1].split()) for k in N if WHO[k] == "nar"),
    sum(len(N[k][1].split()) for k in N if WHO[k] != "nar"))]
open("docs/script_km_en.md", "w").write("\n".join(md))

# ---------------------------------------------------------------- storyboard
md = ["# Storyboard · %s" % PROJ["title_en"], "",
      "Look: **memory drawing**: soft pencil and charcoal on rough, aged paper. Memory scenes are grey with smudges "
      "and tonal hatching; the present day is warm, gentle colour (incense smoke, lotus, morning light). Colour seeps "
      "back into memory during Chapter 10 and returns fully when Malis lights the candle. Archival images appear as old "
      "prints in a family album or in a memorial frame, unaltered. No violence is depicted.", ""]
cur = None
for i, s in enumerate(shots):
    ch = chap(i)
    if ch != cur:
        cur = ch
        md += ["", "## %s · %s %s" % (ch[1], ch[2], ("(" + ch[3] + ")") if ch[3] else ""), ""]
    era = "present (colour)" if s.get("era") == "present" else "memory (grey)"
    md += ["**Shot %d** · %s–%s (%.1f s) · %s · badge: %s" % (i, tc(s["start"]), tc(s["start"] + s["dur"]), s["dur"],
                                                              era, s.get("badge") or "—"),
           "- Setting: " + setting(i),
           "- Figures: " + people(i),
           "- Camera: " + camtxt(s["cam"]),
           "- In: " + TRANS.get(s.get("trans"), s.get("trans") or "soft dissolve") +
           ("; music: %s" % s["music"] if s.get("music") else "") + ("; ambience: %s" % s["amb"] if s.get("amb") else "")
           + ("; sfx: %s" % ", ".join(s["sfx"]) if s.get("sfx") else ""),
           "- Lines: " + (", ".join(s["lines"]) or "—") + (" · note on screen: _%s_" % s["badge_note"]
                                                            if s.get("badge_note") else ""), ""]
open("docs/storyboard.md", "w").write("\n".join(md))

# ---------------------------------------------------------------- shot list
md = ["# Shot list", "", "| # | start | dur | era | badge | lines | transition |", "|---|---|---|---|---|---|---|"]
for i, s in enumerate(shots):
    md.append("| %d | %s | %.1f | %s | %s | %s | %s |" % (i, tc(s["start"]), s["dur"], s.get("era"), s.get("badge") or "",
                                                         ", ".join(s["lines"]), s.get("trans") or ""))
open("docs/shot_list.md", "w").write("\n".join(md))

# ---------------------------------------------------------------- on-screen text
import cards  # noqa: E402
md = ["# On-screen text and captions", "",
      "## Content advisory (0:00)", "",
      "ខ្សែភាពយន្ត នេះ និយាយ អំពី អំពើប្រល័យពូជសាសន៍ និង ការបាត់បង់។ · This film speaks of genocide and loss.",
      "វា មិន បង្ហាញ រូបភាព ហិង្សា ទេ។ · It shows no graphic images.",
      "សូម ឧទ្ទិស ដល់ ជនរងគ្រោះ និង អ្នក នៅ រស់។ · Dedicated to the victims and the survivors.", "",
      "## Title", "", "កម្ពុជាប្រជាធិបតេយ្យ · Democratic Kampuchea · ១៩៧៥–១៩៧៩ · យើងចងចាំ · 1975–1979 · We Remember", "",
      "## Chapter cards (hand-written pencil)", ""]
for (n, km, en, y) in CHS:
    md.append("- ជំពូកទី %d · CHAPTER %d — **%s** / %s — %s" % (n, n, km, en, y))
md += ["", "## Evidence badges (top left, Khmer + English)", ""]
for k, (col, km, en) in cards.BADGES.items():
    if k in ("recon", "memory", "symbol", "photo", "document", "map", "map_recon", "text", "guide"):
        md.append("- `%s`: %s · %s" % (k, km, en))
md += ["", "## Notes under badges, map labels and notebook pages", ""]
for i, s in enumerate(shots):
    if s.get("badge_note"):
        md.append("- %s · shot %d: %s" % (tc(s["start"]), i, s["badge_note"]))
for m in re.finditer(r'NOTE\(\[[^\]]*\], "([^"]+)", "([^"]+)"', src_all):
    md.append("- Notebook page: **%s** / %s" % (m.group(1), m.group(2)))
md += ["", "## Quotation", "",
       "«នៅលើ ផ្លូវ ដ៏ ណែនណាន់តាន់តាប់ ខ្ញុំ ឮ សូរសំឡេង មនុស្សម្នា ស្រែក ហៅ រក ឪពុកម្ដាយ និង បងប្អូន និង សម្រែក ក្មេងៗ "
       "យំ ទារ រក បាយ។» — “On the crowded road, I heard people calling for their parents and relatives, and hungry "
       "children crying for rice.” — Sim Soth (Koy), testimony in Khamboly Dy, *A History of Democratic Kampuchea* "
       "(DC-Cam, 2007), p. 16", "",
       "## Dedication (closing)", "", "កុំ ឲ្យ រឿង នេះ កើត ឡើង ម្ដង ទៀត · Never again", "",
       "## Subtitles", "", "Burned English subtitles (guides in italic, warm colour); soft English and Khmer tracks in "
       "the MP4 and as .srt files in `subtitles/`."]
open("docs/on_screen_text.md", "w").write("\n".join(md))

# ---------------------------------------------------------------- archive and licences
man = json.load(open("archive/manifest.json"))
used = {os.path.basename(e["file"]): e for e in man if e.get("file") and os.path.basename(e["file"]) in SS.USED}
md = ["# Archive images: source, licence and permission status", "",
      "Every image below was opened and checked against its caption. All are public domain or openly licensed; "
      "no permission is needed. Photos are shown unaltered (only scaled and framed). **No S-21 prisoner portraits, "
      "no Vann Nath paintings, and no images of remains or violence are used.**", "",
      "| Shot time | Image | Date | Holder / author | Licence | Source | Permission |", "|---|---|---|---|---|---|---|"]
for i, s in enumerate(shots):
    v = vis_src(i)
    for f in used:
        if '"%s"' % f in v:
            e = used[f]
            md.append("| %s | %s | %s | %s | %s | [file page](%s) | not needed |" % (
                tc(s["start"]), e.get("object_name"), e.get("object_date"), e.get("holding_institution") or
                e.get("author"), e.get("licence"), e.get("source_page_url")))
md += ["", "## Not used, permission required (see research/images.md)", ""]
for e in man:
    if not e.get("file"):
        md.append("- %s — %s — %s" % (e.get("object_name") or e.get("title"), e.get("holding_institution"),
                                      e.get("licence")))
open("docs/archive_and_licences.md", "w").write("\n".join(md))
print("docs written; runtime", tc(total))
