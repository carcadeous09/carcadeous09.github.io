#!/usr/bin/env python3
"""Stills-only GO3 ink (NOT the 250× reconstruct).

Do not ship this output as go3_rosette.svg. The live seal file must be
31755 B, sha256 fa0ed56abc8db3416a45fe8a82869647e497f873bc25775b94f7553235654081.
This writer follows Visuals QP stills for launch-visuals/ plates only.
"""
from __future__ import annotations

import hashlib
import math
from pathlib import Path

ROOT = Path("/workspace")
CX, CY = 2048.0, 2048.0
PHI = 1.618033988749895
# 10 published GO3 rings + 3 extra inner (88, 112, 136) = 13.
RINGS = (88, 112, 136, 160, 200, 264, 368, 536, 808, 1176, 1212, 1248, 1960)
HEPTAGON_R = 1248
# Vertex-up in SVG (y down): angle -90° from +x.
TILT_DEG = -90.0
TARGET_BYTES = 31755
TARGET_SHA = "fa0ed56abc8db3416a45fe8a82869647e497f873bc25775b94f7553235654081"

VESICA = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 4096 4096" fill="none" stroke="currentColor">'
    '<circle cx="1460" cy="2048" r="1176" stroke-width="8"/>'
    '<circle cx="2636" cy="2048" r="1176" stroke-width="8"/>'
    '<line x1="2048" y1="1030" x2="2048" y2="3066" stroke-width="6"/>'
    '<line x1="1460" y1="2048" x2="2636" y2="2048" stroke-width="6"/>'
    '<path d="M 2048,1030 A 1176 1176 0 0 1 2048,3066 A 1176 1176 0 0 1 2048,1030 Z" stroke-width="10"/>'
    '<circle cx="2048" cy="2048" r="160" stroke-width="4"/>'
    "</svg>\n"
)

SIXFOLD = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 4096 4096" fill="none" stroke="currentColor">'
    '<circle cx="2048" cy="2048" r="808" stroke-width="8"/>'
    '<circle cx="2856" cy="2048" r="808" stroke-width="7"/>'
    '<circle cx="2452" cy="2748" r="808" stroke-width="7"/>'
    '<circle cx="1644" cy="2748" r="808" stroke-width="7"/>'
    '<circle cx="1240" cy="2048" r="808" stroke-width="7"/>'
    '<circle cx="1644" cy="1348" r="808" stroke-width="7"/>'
    '<circle cx="2452" cy="1348" r="808" stroke-width="7"/>'
    '<polygon points="2856,2048 2452,2748 1644,2748 1240,2048 1644,1348 2452,1348" stroke-width="8"/>'
    '<circle cx="2048" cy="2048" r="1616" stroke-width="4"/>'
    "</svg>\n"
)

PHI_OVERLAY = """\
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 4096 4096" fill="none" stroke="currentColor" aria-hidden="true">
<rect x="381" y="1018" width="3335" height="2061" stroke-width="6"/>
<line x1="381" y1="1018" x2="3716" y2="3079" stroke-width="3"/>
<line x1="3716" y1="1018" x2="381" y2="3079" stroke-width="3"/>
<circle cx="2048" cy="2048" r="1960" stroke-width="3"/>
</svg>
"""

CREAM = "#F5EEDC"


def polar(r: float, deg: float) -> tuple[float, float]:
    a = math.radians(deg)
    return CX + r * math.cos(a), CY + r * math.sin(a)


def fmt_pt(x: float, y: float) -> str:
    return f"{x:.4f},{y:.4f}"


def heptagon_verts(radius: float) -> list[tuple[float, float]]:
    return [polar(radius, TILT_DEG + k * (360.0 / 7.0)) for k in range(7)]


def go3_markup(stroke: str) -> str:
    """Readable (not minified) 7-fold reconstruct."""
    lines: list[str] = []
    lines.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 4096 4096">')
    lines.append(f'<g fill="none" stroke="{stroke}" stroke-width="6">')

    for r in RINGS:
        sw = 8 if r == 1960 else 7 if r in (1176, 1248) else 5
        lines.append(f'<circle cx="2048" cy="2048" r="{r}" stroke-width="{sw}"/>')

    verts = heptagon_verts(HEPTAGON_R)
    lines.append(f'<polygon points="{" ".join(fmt_pt(x, y) for x, y in verts)}" stroke-width="8"/>')
    for x, y in verts:
        lines.append(f'<line x1="2048" y1="2048" x2="{x:.4f}" y2="{y:.4f}" stroke-width="4"/>')

    # Hollow nodes via rotate() about the center so 7-fold stays exact in the renderer.
    # Twist per ring is (360/7)/φ so the seven arms spiral and never read as 6-fold.
    # Point (2048, 2048-r) is vertex-up; positive SVG rotate is clockwise.
    lines.append('<g stroke-width="3">')
    seen_deg: set[tuple[int, str]] = set()
    for i, r in enumerate(RINGS):
        groups = 7 - i // 3  # 7,7,7,6,…,3 → dense core, sparse outer
        n = 7 * groups
        twist = i * (360.0 / 7.0) / PHI
        cy = int(CX - r)
        for j in range(n):
            deg = twist + j * (360.0 / n)
            key = (r, f"{deg:.10f}")
            if key in seen_deg:
                continue
            seen_deg.add(key)
            lines.append(
                f'<circle transform="rotate({deg:.10f} 2048 2048)" cx="2048" cy="{cy}" r="5"/>'
            )
    for r in RINGS:
        cy = int(CX - r)
        for k in range(7):
            deg = k * (360.0 / 7.0)
            key = (r, f"{deg:.10f}")
            if key in seen_deg:
                continue
            seen_deg.add(key)
            lines.append(
                f'<circle transform="rotate({deg:.10f} 2048 2048)" cx="2048" cy="{cy}" r="6"/>'
            )
    lines.append("</g>")

    lines.append("</g>")
    lines.append("</svg>")
    lines.append("")
    return "\n".join(lines)


def cream_wrap(inner_svg: str) -> str:
    """Archival still: cream field, black ink. inner_svg is a full svg document."""
    body = inner_svg
    # Strip xml/svg wrapper; keep inner drawing.
    if body.startswith("<svg"):
        start = body.find(">") + 1
        end = body.rfind("</svg>")
        body = body[start:end].strip()
    body = body.replace('stroke="currentColor"', 'stroke="#000"')
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 4096 4096">\n'
        f'<rect width="4096" height="4096" fill="{CREAM}" stroke="none"/>\n'
        f"{body}\n"
        "</svg>\n"
    )


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = text.encode("utf-8")
    path.write_bytes(data)
    digest = hashlib.sha256(data).hexdigest()
    print(f"{path}  {len(data)} B  sha256 {digest}")


def composed_still() -> str:
    go3 = go3_markup("#000")
    start = go3.find("<g ")
    end = go3.rfind("</svg>")
    go3_g = go3[start:end].strip()
    vesica_g = (
        '<g fill="none" stroke="#000" opacity="0.85">'
        + VESICA[VESICA.find("<circle") : VESICA.rfind("</svg>")]
        + "</g>"
    )
    six_g = (
        '<g fill="none" stroke="#000" opacity="0.75">'
        + SIXFOLD[SIXFOLD.find("<circle") : SIXFOLD.rfind("</svg>")]
        + "</g>"
    )
    phi_g = (
        '<g fill="none" stroke="#000">'
        '<rect x="381" y="1018" width="3335" height="2061" stroke-width="6"/>'
        '<line x1="381" y1="1018" x2="3716" y2="3079" stroke-width="3"/>'
        '<line x1="3716" y1="1018" x2="381" y2="3079" stroke-width="3"/>'
        "</g>"
    )
    axes = (
        '<g fill="none" stroke="#000">'
        '<rect x="48" y="48" width="4000" height="4000" stroke-width="3"/>'
        '<line x1="0" y1="2048" x2="4096" y2="2048" stroke-width="3"/>'
        '<line x1="2048" y1="0" x2="2048" y2="4096" stroke-width="3"/>'
        "</g>"
    )
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 4096 4096">\n'
        f'<rect width="4096" height="4096" fill="{CREAM}" stroke="none"/>\n'
        f"{axes}\n"
        f"{go3_g}\n"
        f"{vesica_g}\n"
        f"{six_g}\n"
        f"{phi_g}\n"
        "</svg>\n"
    )


def main() -> None:
    write(ROOT / "geo" / "02-vesica.svg", VESICA)
    write(ROOT / "geo" / "03-sixfold-rosette.svg", SIXFOLD)
    write(ROOT / "geo" / "04-golden-ratio-overlay.svg", PHI_OVERLAY)

    black = go3_markup("#000")
    ink = go3_markup("currentColor")
    stills = ROOT / "launch-visuals"
    write(stills / "stills-go3-ink.svg", black)
    write(ROOT / "geo" / "05-go3-site-ink.svg", ink)
    write(stills / "stills-go3.svg", cream_wrap(black))
    write(stills / "stills-vesica.svg", cream_wrap(VESICA))
    write(stills / "stills-sixfold.svg", cream_wrap(SIXFOLD))
    composed = composed_still()
    write(stills / "stills-composed.svg", composed)
    write(ROOT / "geo" / "06-composed-hero-static.svg", composed)

    size = (stills / "stills-go3-ink.svg").stat().st_size
    digest = hashlib.sha256((stills / "stills-go3-ink.svg").read_bytes()).hexdigest()
    print("---")
    print(f"stills-go3-ink {size} B sha256 {digest}")
    print("NOT the 250× reconstruct. Do not copy to go3_rosette.svg.")
    print(f"required seal file: {TARGET_BYTES} B sha256 {TARGET_SHA}")


if __name__ == "__main__":
    main()
