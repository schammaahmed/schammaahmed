"""Animated ASCII laptop with a robot face on the screen.

The laptop is pure ASCII (no box-drawing characters) so it stays aligned in any
monospace font. The face is drawn separately and centre-anchored rather than
placed on the character grid, so it can be a larger size than the chassis.

Frame cycling uses animation-fill-mode: none on purpose. During its delay each
frame falls back to its own style (opacity 0), so at t=0 exactly one frame is
visible - FRAMES[0]. A renderer that freezes SVG animation at t=0 therefore
still shows a complete, correct face instead of a blank or stacked mess.

STATIC=1 emits just that first frame with no animation.
"""

import os

HERE = os.path.dirname(__file__)
OUT = os.path.join(HERE, "..", "assets", "robot.svg")

STATIC = os.environ.get("STATIC") == "1"

W, H = 360, 344

BG = "#0d1117"
BORDER = "#21262d"
CHASSIS = "#8b949e"
SCREEN_BG = "#0a1a12"
GLOW = "#39d353"
MUTED = "#7d8590"

FONT = ("ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, "
        "'Liberation Mono', monospace")

ART_SIZE = 13.0
CHAR_W = ART_SIZE * 0.6   # advance width of a monospace glyph
LINE_H = 16.5
CAPTION_GAP = 28.0

# Laptop chassis. Row/col coordinates of the screen interior are derived from
# SCREEN_ROWS / SCREEN_COLS below, so keep them in sync if you redraw this.
ART = [
    "   .----------------------------------.   ",
    "   |  .----------------------------.  |   ",
    "   |  |                            |  |   ",
    "   |  |                            |  |   ",
    "   |  |                            |  |   ",
    "   |  |                            |  |   ",
    "   |  |                            |  |   ",
    "   |  |                            |  |   ",
    "   |  '----------------------------'  |   ",
    "   |              .----.              |   ",
    "   '----------------------------------'   ",
    " .--------------------------------------. ",
    "/                                        \\",
    "'----------------------------------------'",
]

SCREEN_ROWS = (2, 7)    # inclusive text-row span of the screen interior
SCREEN_COLS = (7, 34)   # inclusive column span of the screen interior

# (eye, eye colour). The mouth is always "w" - a wide-set two-line face read as
# a grimace, so the face is a single compact kaomoji instead. Frame 0 is the
# resting face and the one a frozen renderer shows, hence the heart eyes.
HEART = "♥"
BLUSH = "#ff6b81"
FRAMES = [
    (HEART, BLUSH),
    (HEART, BLUSH),
    ("^", GLOW),
    ("-", GLOW),
]
MOUTH = "w"
CYCLE = 5.2  # seconds for one full pass through FRAMES

CAPTION = "building things"


def esc(text):
    return (str(text).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;"))


def build():
    art_w = max(len(line) for line in ART) * CHAR_W
    art_x = (W - art_w) / 2.0
    # Centre the chassis + caption block vertically. ART_SIZE * 0.85 approximates
    # the ascender above the first baseline.
    block_h = (len(ART) - 1) * LINE_H + CAPTION_GAP + ART_SIZE * 0.85
    art_y = (H - block_h) / 2.0 + ART_SIZE * 0.85

    # screen interior in user units
    sx0 = art_x + SCREEN_COLS[0] * CHAR_W
    sx1 = art_x + (SCREEN_COLS[1] + 1) * CHAR_W
    # Nudge past the glyph bodies of the border rows so the backlight fills the
    # bezel instead of stopping a whole line short of it.
    sy0 = art_y + (SCREEN_ROWS[0] - 1) * LINE_H + 2
    sy1 = art_y + (SCREEN_ROWS[1] + 1) * LINE_H - 10
    cx = (sx0 + sx1) / 2.0

    out = []
    out.append(
        '<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        'viewBox="0 0 {w} {h}" role="img" '
        'aria-label="ASCII laptop with a smiling robot face on the screen">'
        .format(w=W, h=H)
    )

    frame_css = ""
    if not STATIC:
        pct = 100.0 / len(FRAMES)
        frame_css = """
    .frame { opacity: 0; animation: cyc %ss steps(1) infinite; }
    @keyframes cyc { 0%%   { opacity: 1; }
                     %.4f%% { opacity: 0; }
                     100%% { opacity: 0; } }
    .cursor { animation: blink 1s steps(1) infinite; }
    @keyframes blink { 50%% { opacity: 0; } }
    .led { animation: pulse 2.4s ease-in-out infinite; }
    @keyframes pulse { 0%%, 100%% { opacity: .35; } 50%% { opacity: 1; } }
    .bob { animation: bob 2.6s ease-in-out infinite; }
    @keyframes bob { 0%%, 100%% { transform: translateY(0); }
                     50%%       { transform: translateY(-3px); } }
    @media (prefers-reduced-motion: reduce) {
      .frame { animation: none; }
      .frame0 { opacity: 1; }
      .cursor, .led, .bob { animation: none; }
    }""" % (CYCLE, pct)

    out.append(
        '<style>text{{font-family:{f};white-space:pre;}}{c}</style>'
        .format(f=FONT, c=frame_css)
    )

    out.append(
        '<rect width="{w}" height="{h}" rx="10" fill="{bg}" stroke="{br}"/>'
        .format(w=W, h=H, bg=BG, br=BORDER)
    )

    # screen backlight
    out.append(
        '<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="3" '
        'fill="{s}"/>'.format(x=sx0, y=sy0, w=sx1 - sx0, h=sy1 - sy0, s=SCREEN_BG)
    )

    # chassis
    for i, line in enumerate(ART):
        out.append(
            '<text x="{x:.1f}" y="{y:.1f}" font-size="{fs}" fill="{c}" '
            'xml:space="preserve">{t}</text>'
            .format(x=art_x, y=art_y + i * LINE_H, fs=ART_SIZE, c=CHASSIS,
                    t=esc(line))
        )

    # power LED on the base
    out.append(
        '<circle cx="{x:.1f}" cy="{y:.1f}" r="2.6" fill="{g}"{c}/>'
        .format(x=art_x + 4 * CHAR_W, y=art_y + 12 * LINE_H - 4, g=GLOW,
                c="" if STATIC else ' class="led"')
    )

    # face: one compact kaomoji, bobbing
    face_size = 40.0
    face_y = sy0 + (sy1 - sy0) * 0.62
    out.append('<g{}>'.format("" if STATIC else ' class="bob"'))

    frames = FRAMES[:1] if STATIC else FRAMES
    for i, (eye, eye_colour) in enumerate(frames):
        cls = "" if STATIC else ' class="frame frame{}"'.format(i)
        delay = "" if STATIC else ' style="animation-delay:{:.3f}s"'.format(
            CYCLE * i / float(len(FRAMES)))
        out.append(
            '<text x="{x:.1f}" y="{y:.1f}" font-size="{fs}" '
            'text-anchor="middle" xml:space="preserve"{c}{d}>'
            '<tspan fill="{e}">{eye}</tspan>'
            '<tspan fill="{g}">{m}</tspan>'
            '<tspan fill="{e}">{eye}</tspan></text>'
            .format(x=cx, y=face_y, fs=face_size, c=cls, d=delay,
                    e=eye_colour, g=GLOW, eye=esc(eye), m=esc(MOUTH))
        )

    out.append("</g>")

    # caption line under the laptop
    caption_y = art_y + len(ART) * LINE_H + 26
    out.append(
        '<text x="{x:.1f}" y="{y:.1f}" font-size="12.5" fill="{m}" '
        'text-anchor="middle">$ {t} <tspan fill="{g}"{c}>&#9611;</tspan></text>'
        .format(x=W / 2.0, y=caption_y, m=MUTED, g=GLOW, t=esc(CAPTION),
                c="" if STATIC else ' class="cursor"')
    )

    out.append("</svg>")
    return "\n".join(out)


def main():
    widths = set(len(line) for line in ART)
    if len(widths) > 1:
        print("note: chassis rows have ragged widths {} - "
              "right edge will look uneven".format(sorted(widths)))
    svg = build()
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w") as fh:
        fh.write(svg)
    print("wrote {} ({:,} bytes)".format(os.path.relpath(OUT), len(svg)))


if __name__ == "__main__":
    main()
