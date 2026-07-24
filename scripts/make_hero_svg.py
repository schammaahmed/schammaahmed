"""Composite the robot and the info card into one SVG.

Two side-by-side <img> tags in a README wrap the moment the container is
narrower than their combined width, and GitHub's profile README panel is
narrower than 850px. A single image cannot wrap - it just scales down - so the
two panels are nested here as child <svg> elements, each keeping its own
coordinate system and its own <style> block.

Run this after make_robot_svg.py and make_info_card.py; it reads their output.
"""

import os
import re

HERE = os.path.dirname(__file__)
ASSETS = os.path.join(HERE, "..", "assets")
OUT = os.path.join(ASSETS, "hero.svg")

GAP = 0  # panels already carry their own padding

PARTS = ["robot.svg", "info-card.svg"]

OPEN_SVG = re.compile(r"<svg\b[^>]*>", re.S)


def dimension(head, attr, name):
    match = re.search(r'\b{}="([\d.]+)"'.format(attr), head)
    if not match:
        raise SystemExit("{}: <svg> has no numeric {}".format(name, attr))
    return float(match.group(1))


def load(name):
    """Return (width, height, inner markup) for a generated panel."""
    with open(os.path.join(ASSETS, name)) as fh:
        svg = fh.read()

    match = OPEN_SVG.search(svg)
    if not match:
        raise SystemExit("{}: no <svg> element found".format(name))

    head = match.group(0)
    return (dimension(head, "width", name),
            dimension(head, "height", name),
            svg[match.end():svg.rindex("</svg>")])


def build():
    panels = [load(name) for name in PARTS]

    total_w = sum(p[0] for p in panels) + GAP * (len(panels) - 1)
    total_h = max(p[1] for p in panels)

    out = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="{w:.0f}" height="{h:.0f}" '
        'viewBox="0 0 {w:.0f} {h:.0f}" role="img" '
        'aria-label="Schamma Ahmed: ASCII laptop with a robot face, and a '
        'summary card of current work, stack and links">'
        .format(w=total_w, h=total_h)
    ]

    x = 0.0
    for width, height, inner in panels:
        out.append(
            '<svg x="{x:.0f}" y="0" width="{w:.0f}" height="{h:.0f}" '
            'viewBox="0 0 {w:.0f} {h:.0f}">'.format(x=x, w=width, h=height)
        )
        out.append(inner.strip())
        out.append("</svg>")
        x += width + GAP

    out.append("</svg>")
    return total_w, total_h, "\n".join(out)


def main():
    width, height, svg = build()
    with open(OUT, "w") as fh:
        fh.write(svg)
    print("wrote {} ({:.0f}x{:.0f}, {:,} bytes)"
          .format(os.path.relpath(OUT), width, height, len(svg)))


if __name__ == "__main__":
    main()
