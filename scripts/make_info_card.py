"""Hand-authored neofetch-style info card as an animated SVG.

Edit PROFILE below - everything else is layout. Values render in a monospace
column ~50 characters wide; longer strings will overflow the card.

STATIC=1 disables the animation.
"""

import os

HERE = os.path.dirname(__file__)
OUT = os.path.join(HERE, "..", "assets", "info-card.svg")

STATIC = os.environ.get("STATIC") == "1"

PROMPT = "schamma@github ~ $ neofetch"

PROFILE = [
    ("Now", "Software engineering intern · building in public"),
    ("Focus", "Backend systems, REST APIs, infrastructure"),
    ("Stack", "Java · Spring Boot · React · PostgreSQL · Docker"),
    ("Shipping", "Point of sale system for a youth organisation"),
    ("Also", "Sukoon — fragrance discovery, built for one"),
    ("Learning", "Java SE Associate · Meta Front-End"),
    ("Site", "schammaahmed.com"),
    ("LinkedIn", "www.linkedin.com/in/schammaahmed"),
]

MOTTO = "Améliorer. Always improving. Always figuring it out."

# H must match the ASCII portrait's height so the README table rows line up.
W, H = 490, 344
PAD = 20
KEY_X = PAD
VAL_X = PAD + 86
ROW_TOP = 78
ROW_PITCH = 26

BG = "#0d1117"
BORDER = "#21262d"
FG = "#c9d1d9"
MUTED = "#7d8590"
KEY = "#58a6ff"
ACCENT = "#39d353"

FONT = ("ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, "
        "'Liberation Mono', monospace")


def esc(text):
    return (str(text).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;"))


def build():
    out = []
    out.append(
        '<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        'viewBox="0 0 {w} {h}" role="img" '
        'aria-label="Profile summary card for Schamma Ahmed">'.format(w=W, h=H)
    )

    # See render_heatmap_svg.py: "backwards", not "both", so the settled state
    # survives renderers that ignore CSS animation inside <img>.
    anim = "" if STATIC else """
    .row { animation: slide .5s cubic-bezier(.2,.7,.3,1) backwards; }
    @keyframes slide { from { opacity: 0; transform: translateX(-10px); }
                       to   { opacity: 1; transform: none; } }
    .cursor { animation: blink 1.1s steps(1) infinite; }
    @keyframes blink { 50% { opacity: 0; } }
    @media (prefers-reduced-motion: reduce) {
      .row, .cursor { animation: none; }
    }"""

    out.append('<style>text{{font-family:{f};}}{a}</style>'.format(f=FONT, a=anim))
    out.append(
        '<rect width="{w}" height="{h}" rx="10" fill="{bg}" stroke="{br}"/>'
        .format(w=W, h=H, bg=BG, br=BORDER)
    )

    cls = "" if STATIC else ' class="row"'

    def delay(i):
        return "" if STATIC else ' style="animation-delay:{:.2f}s"'.format(0.1 + i * 0.09)

    # window chrome
    for i, colour in enumerate(("#ff5f56", "#ffbd2e", "#27c93f")):
        out.append('<circle cx="{x}" cy="24" r="5.5" fill="{c}" opacity=".85"/>'
                   .format(x=PAD + 6 + i * 17, c=colour))

    out.append(
        '<text x="{x}" y="{y}" fill="{fg}" font-size="12.5"{c}{d}>{t}</text>'
        .format(x=PAD + 66, y=28, fg=FG, c=cls, d=delay(0), t=esc(PROMPT))
    )
    out.append('<line x1="{a}" y1="46" x2="{b}" y2="46" stroke="{br}"/>'
               .format(a=PAD, b=W - PAD, br=BORDER))

    for i, (key, value) in enumerate(PROFILE):
        y = ROW_TOP + i * ROW_PITCH
        d = delay(i + 1)
        out.append(
            '<text x="{x}" y="{y}" fill="{k}" font-size="12.5" '
            'font-weight="600"{c}{d}>{t}</text>'
            .format(x=KEY_X, y=y, k=KEY, c=cls, d=d, t=esc(key))
        )
        out.append(
            '<text x="{x}" y="{y}" fill="{fg}" font-size="12.5"{c}{d}>{t}</text>'
            .format(x=VAL_X, y=y, fg=FG, c=cls, d=d, t=esc(value))
        )

    divider_y = ROW_TOP + (len(PROFILE) - 1) * ROW_PITCH + 22
    out.append('<line x1="{a}" y1="{y}" x2="{b}" y2="{y}" stroke="{br}"/>'
               .format(a=PAD, b=W - PAD, y=divider_y, br=BORDER))
    out.append(
        '<text x="{x}" y="{y}" fill="{m}" font-size="11.5" '
        'font-style="italic"{c}{d}>{t}</text>'
        .format(x=PAD, y=divider_y + 22, m=MUTED, c=cls,
                d=delay(len(PROFILE) + 1), t=esc(MOTTO))
    )

    prompt_y = divider_y + 48
    out.append(
        '<text x="{x}" y="{y}" fill="{a}" font-size="12.5"{c}{d}>$ '
        '<tspan fill="{fg}" class="cursor">▋</tspan></text>'
        .format(x=PAD, y=prompt_y, a=ACCENT, fg=FG, c=cls, d=delay(len(PROFILE) + 2))
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
