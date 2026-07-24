"""Project showcase strip - one animated card per public project.

Not part of the original article; added so the profile links to real work
instead of trophy badges. Cards are laid out evenly across the full width so
the strip lines up with the heatmap above it.

STATIC=1 disables the animation.
"""

import os

HERE = os.path.dirname(__file__)
OUT = os.path.join(HERE, "..", "assets", "showcase.svg")

STATIC = os.environ.get("STATIC") == "1"

PROJECTS = [
    {
        "name": "pos",
        "tagline": "Point of sale system for a youth organisation",
        "blurb": "Sellers, tabs and till reconciliation,\nrunning at a real organisation.",
        "stack": ["Java", "Spring Boot", "React", "Postgres"],
        "accent": "#39d353",
    },
    {
        "name": "sukoon",
        "tagline": "Fragrance discovery, done properly",
        "blurb": "Built for one person's taste,\nnot an average of everyone's.",
        "stack": ["TypeScript", "React", "Design"],
        "accent": "#d2a8ff",
    },
]

W = 850
PAD = 22
GAP = 18
H = 186

BG = "#0d1117"
BORDER = "#21262d"
CARD_BG = "#12181f"
FG = "#c9d1d9"
MUTED = "#7d8590"
CHIP_BG = "#1c2530"

FONT = ("ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, "
        "'Liberation Mono', monospace")

CHAR_W = 6.0  # approx advance width for 10px monospace, used to size chips


def esc(text):
    return (str(text).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;"))


def build():
    n = len(PROJECTS)
    inner = W - PAD * 2
    card_w = (inner - GAP * (n - 1)) / float(n)
    card_top = 54
    card_h = H - card_top - PAD

    out = []
    out.append(
        '<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        'viewBox="0 0 {w} {h}" role="img" '
        'aria-label="Featured projects: {names}">'
        .format(w=W, h=H, names=esc(", ".join(p["name"] for p in PROJECTS)))
    )

    # See render_heatmap_svg.py: "backwards", not "both", so the settled state
    # survives renderers that ignore CSS animation inside <img>.
    anim = "" if STATIC else """
    .card { animation: rise .55s cubic-bezier(.2,.7,.3,1) backwards; }
    .line { animation: fade .5s ease-out backwards; }
    @keyframes rise { from { opacity: 0; transform: translateY(14px); }
                      to   { opacity: 1; transform: none; } }
    @keyframes fade { from { opacity: 0; } to { opacity: 1; } }
    @media (prefers-reduced-motion: reduce) {
      .card, .line { animation: none; }
    }"""

    out.append('<style>text{{font-family:{f};}}{a}</style>'.format(f=FONT, a=anim))
    out.append(
        '<rect width="{w}" height="{h}" rx="10" fill="{bg}" stroke="{br}"/>'
        .format(w=W, h=H, bg=BG, br=BORDER)
    )

    line_cls = "" if STATIC else ' class="line"'
    out.append(
        '<text x="{x}" y="34" fill="{fg}" font-size="14"{c}>'
        '<tspan fill="#39d353">$</tspan> ls ~/projects --public</text>'
        .format(x=PAD, fg=FG, c=line_cls)
    )

    for i, project in enumerate(PROJECTS):
        x = PAD + i * (card_w + GAP)
        card_cls = "" if STATIC else ' class="card"'
        style = "" if STATIC else ' style="animation-delay:{:.2f}s"'.format(
            0.25 + i * 0.14)

        out.append(
            '<rect x="{x:.1f}" y="{y}" width="{w:.1f}" height="{h:.1f}" rx="8" '
            'fill="{bg}" stroke="{br}"{c}{s}/>'
            .format(x=x, y=card_top, w=card_w, h=card_h,
                    bg=CARD_BG, br=BORDER, c=card_cls, s=style)
        )
        # accent spine
        out.append(
            '<rect x="{x:.1f}" y="{y}" width="3" height="{h:.1f}" rx="1.5" '
            'fill="{a}"{c}{s}/>'
            .format(x=x, y=card_top, h=card_h, a=project["accent"],
                    c=card_cls, s=style)
        )

        tx = x + 16
        out.append(
            '<text x="{x:.1f}" y="{y}" fill="{a}" font-size="15" '
            'font-weight="700"{c}{s}>{t}</text>'
            .format(x=tx, y=card_top + 28, a=project["accent"],
                    c=card_cls, s=style, t=esc(project["name"]))
        )
        out.append(
            '<text x="{x:.1f}" y="{y}" fill="{fg}" font-size="11.5"{c}{s}>{t}</text>'
            .format(x=tx, y=card_top + 47, fg=FG, c=card_cls, s=style,
                    t=esc(project["tagline"]))
        )

        for j, blurb_line in enumerate(project["blurb"].split("\n")):
            out.append(
                '<text x="{x:.1f}" y="{y}" fill="{m}" font-size="10.5"{c}{s}>{t}</text>'
                .format(x=tx, y=card_top + 68 + j * 14, m=MUTED,
                        c=card_cls, s=style, t=esc(blurb_line))
            )

        chip_x = tx
        chip_y = card_top + card_h - 26
        for tech in project["stack"]:
            chip_w = len(tech) * CHAR_W + 14
            if chip_x + chip_w > x + card_w - 12:
                break
            out.append(
                '<rect x="{x:.1f}" y="{y}" width="{w:.1f}" height="18" rx="9" '
                'fill="{bg}"{c}{s}/>'
                .format(x=chip_x, y=chip_y, w=chip_w, bg=CHIP_BG,
                        c=card_cls, s=style)
            )
            out.append(
                '<text x="{x:.1f}" y="{y}" fill="{m}" font-size="10"{c}{s}>{t}</text>'
                .format(x=chip_x + 7, y=chip_y + 12.5, m=MUTED,
                        c=card_cls, s=style, t=esc(tech))
            )
            chip_x += chip_w + 6

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
