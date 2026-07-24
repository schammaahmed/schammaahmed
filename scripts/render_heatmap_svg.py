"""Render contributions.json as a self-contained animated SVG.

GitHub strips <script> and external CSS from READMEs but renders SVG, and CSS
keyframes inside an SVG still run when it is loaded as an <img>. So all motion
here is declarative CSS that plays once and freezes on the final frame.

STATIC=1 emits the same SVG with animation disabled (useful for diffing).
"""

import datetime
import json
import os

HERE = os.path.dirname(__file__)
DATA = os.path.join(HERE, "..", "data", "contributions.json")
OUT = os.path.join(HERE, "..", "assets", "contrib-heatmap.svg")

STATIC = os.environ.get("STATIC") == "1"

W = 850
PAD = 22
LABEL_W = 30
GRID_TOP = 74
ROWS = 7

BG = "#0d1117"
BORDER = "#21262d"
FG = "#c9d1d9"
MUTED = "#7d8590"
ACCENT = "#39d353"

# level 0-4, then a brighter tone reserved for the single best day
LEVELS = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]
PEAK = "#69f0a0"

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

FONT = ("ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, "
        "'Liberation Mono', monospace")


def esc(text):
    return (str(text).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;"))


def plural(n, word):
    return "{:,} {}{}".format(n, word, "" if n == 1 else "s")


def build():
    with open(DATA) as fh:
        data = json.load(fh)

    days = data["days"]
    first = datetime.date.fromisoformat(days[0]["date"])
    # Calendar columns start on Sunday; back up to the Sunday on or before day 1.
    start = first - datetime.timedelta(days=(first.weekday() + 1) % 7)

    placed = []
    for day in days:
        d = datetime.date.fromisoformat(day["date"])
        delta = (d - start).days
        placed.append((delta // 7, delta % 7, d, day))

    cols = max(p[0] for p in placed) + 1
    pitch = (W - PAD * 2 - LABEL_W) / float(cols)
    cell = pitch - 2.7
    grid_x = PAD + LABEL_W
    grid_h = ROWS * pitch
    footer_y = GRID_TOP + grid_h + 34
    height = int(footer_y + 22)

    peak_date = data["best_day"]["date"]
    out = []

    out.append(
        '<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        'viewBox="0 0 {w} {h}" role="img" '
        'aria-label="GitHub contribution heatmap for {u}: {t} contributions in the last year">'
        .format(w=W, h=height, u=esc(data["username"]), t=data["total"])
    )

    # animation-fill-mode is "backwards", never "both": the settled state is the
    # element's own style, so if a renderer ignores CSS animation in <img> the
    # card still shows its final frame instead of a blank box.
    anim = "" if STATIC else """
    .cell   { transform-box: fill-box; transform-origin: center;
              animation: pop .45s ease-out backwards; }
    .fade   { animation: fade .6s ease-out backwards; }
    @keyframes pop  { from { opacity: 0; transform: translateY(-6px) scale(.4); }
                      to   { opacity: 1; transform: none; } }
    @keyframes fade { from { opacity: 0; } to { opacity: 1; } }
    @media (prefers-reduced-motion: reduce) {
      .cell, .fade { animation: none; }
    }"""

    out.append(
        '<style>text{{font-family:{font};}}{anim}</style>'.format(font=FONT, anim=anim)
    )

    out.append(
        '<rect width="{w}" height="{h}" rx="10" fill="{bg}" stroke="{br}"/>'
        .format(w=W, h=height, bg=BG, br=BORDER)
    )

    # ---- header ----
    cls = "" if STATIC else ' class="fade"'
    out.append(
        '<text x="{x}" y="34" fill="{fg}" font-size="14"{c}>'
        '<tspan fill="{a}">$</tspan> git log --graph --since="1 year ago"</text>'
        .format(x=PAD, fg=FG, a=ACCENT, c=cls)
    )
    out.append(
        '<text x="{x}" y="34" text-anchor="end" fill="{m}" font-size="12"{c}>{t}</text>'
        .format(x=W - PAD, m=MUTED, c=cls,
                t=esc(plural(data["total"], "contribution")))
    )

    # ---- month labels ----
    seen = set()
    for col, row, d, _ in placed:
        if d.month in seen or d.day > 7:
            continue
        seen.add(d.month)
        x = grid_x + col * pitch
        if x > W - PAD - 26:
            continue
        style = "" if STATIC else ' style="animation-delay:{:.2f}s"'.format(
            0.25 + col * 0.012)
        out.append(
            '<text x="{x:.1f}" y="{y}" fill="{m}" font-size="10"{c}{s}>{t}</text>'
            .format(x=x, y=GRID_TOP - 8, m=MUTED, c=cls, s=style, t=MONTHS[d.month - 1])
        )

    # ---- weekday labels ----
    for row, label in ((1, "Mon"), (3, "Wed"), (5, "Fri")):
        style = "" if STATIC else ' style="animation-delay:.3s"'
        out.append(
            '<text x="{x}" y="{y:.1f}" fill="{m}" font-size="10"{c}{s}>{t}</text>'
            .format(x=PAD, y=GRID_TOP + row * pitch + cell * 0.78,
                    m=MUTED, c=cls, s=style, t=label)
        )

    # ---- grid ----
    for col, row, d, day in placed:
        fill = PEAK if day["date"] == peak_date else LEVELS[min(day["level"], 4)]
        x = grid_x + col * pitch
        y = GRID_TOP + row * pitch
        # diagonal wipe: delay grows with column, nudged by row
        style = "" if STATIC else ' style="animation-delay:{:.3f}s"'.format(
            0.3 + col * 0.016 + row * 0.03)
        cell_cls = "" if STATIC else ' class="cell"'
        label = "{}: {}".format(day["date"], plural(day["count"], "contribution"))
        out.append(
            '<rect x="{x:.1f}" y="{y:.1f}" width="{s:.1f}" height="{s:.1f}" rx="2.5" '
            'fill="{f}"{c}{st}><title>{l}</title></rect>'
            .format(x=x, y=y, s=cell, f=fill, c=cell_cls, st=style, l=esc(label))
        )

    # ---- footer: stats left, legend right ----
    tail = "" if STATIC else ' style="animation-delay:1.5s"'
    stats = "{}  ·  {} active  ·  streak {}  ·  best {} on {}".format(
        plural(data["total"], "contribution"),
        data["active_days"],
        data["current_streak"],
        data["best_day"]["count"],
        data["best_day"]["date"],
    )
    out.append(
        '<text x="{x}" y="{y:.0f}" fill="{m}" font-size="11"{c}{s}>{t}</text>'
        .format(x=PAD, y=footer_y, m=MUTED, c=cls, s=tail, t=esc(stats))
    )

    legend_x = W - PAD - 5 * 14 - 58
    out.append(
        '<text x="{x:.0f}" y="{y:.0f}" fill="{m}" font-size="11"{c}{s}>Less</text>'
        .format(x=legend_x, y=footer_y, m=MUTED, c=cls, s=tail)
    )
    for i, colour in enumerate(LEVELS):
        out.append(
            '<rect x="{x:.0f}" y="{y:.0f}" width="10" height="10" rx="2.5" '
            'fill="{f}"{c}{s}/>'
            .format(x=legend_x + 30 + i * 14, y=footer_y - 9, f=colour, c=cls, s=tail)
        )
    out.append(
        '<text x="{x:.0f}" y="{y:.0f}" fill="{m}" font-size="11"{c}{s}>More</text>'
        .format(x=legend_x + 30 + 5 * 14 + 4, y=footer_y, m=MUTED, c=cls, s=tail)
    )

    out.append("</svg>")
    return "\n".join(out)


def main():
    svg = build()
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w") as fh:
        fh.write(svg)
    print("wrote {} ({:,} bytes)".format(os.path.relpath(OUT), len(svg)))


if __name__ == "__main__":
    main()
