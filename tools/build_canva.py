"""Build the Canva-importable variant of the portfolio.

Canva Code 2.0 (July 2026) can import a standalone ``.html`` file, but its own
help page lists what does not survive the import:

    * "JavaScript functionality is not supported with imported designs"
    * "The style / complex CSS may not be converted exactly"
    * "Very large HTML files may take longer to be processed"

This script produces a static twin of the portfolio that is designed around
those limits, while keeping the same template as the real site:

1. **No JavaScript at all.**  Every ``<script>`` block is dropped, including
   the four inlined animation libraries.
2. **No motion layer.**  Anything between ``motion:start`` / ``motion:end``
   markers goes: the preloader, progress bar, pointer aura, marquee band and
   the pinned-hero CSS.  None of it can work without JS, and the pinned hero
   would leave a screen of empty scroll behind.
3. **Nothing hidden behind JS.**  Every reveal rule is scoped to ``.js`` on the
   template, so the Canva copy renders everything visible by default.
4. **No JS-driven gallery.**  The thumbnail strip needed JS to swap the large
   screenshot, so each project shows both screenshots as plain captioned
   figures instead.  Nothing is clickable, nothing is hidden, and each image is
   referenced once instead of 10 times, which is what keeps the file small
   enough for Canva to process (1.38 MB -> ~0.55 MB).
5. **No JS-driven menu.**  The hamburger could never open without JS, so the
   nav is a always-visible wrapped row instead.

Usage:
    python tools/build_canva.py
"""

import base64
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = ROOT / "portfolio_assets" / "portfolio.template.html"
IMAGES = ROOT / "portfolio_assets" / "opt"
OUTPUT = ROOT / "Christian-Jade-Badua-Portfolio-Canva.html"

# project key -> (main image, main caption, second image, second caption, alt)
PROJECTS = {
    "bhims": {
        "main": "bhims-landing",
        "main_caption": "Landing page",
        "second": "bhims-listings",
        "second_caption": "Listings page",
    },
    "cis": {
        "main": "cis-dashboard",
        "main_caption": "Dashboard",
        "second": "cis-home",
        "second_caption": "Sign-in home",
    },
}

FIGCAPTION_CSS = (
    "/* Canva build: captions stand in for the JS thumbnail strip */\n"
    ".shot figcaption{\n"
    "  font-size:.72rem;font-weight:600;letter-spacing:.1em;text-transform:uppercase;\n"
    "  color:var(--faint);padding:.6rem .8rem;border-top:1px solid rgba(255,255,255,.08);\n"
    "  background:rgba(0,0,0,.28);\n"
    "}\n"
)


def sub_once(pattern, replacement, text, label, flags=0):
    """Replace exactly one occurrence, or stop the build."""
    new, n = re.subn(pattern, replacement, text, flags=flags)
    if n != 1:
        sys.exit(f"[FAIL] expected 1 match for {label}, found {n}")
    print(f"[OK]   {label}")
    return new


def main() -> int:
    if not TEMPLATE.exists():
        print(f"[FAIL] template not found: {TEMPLATE}")
        return 1

    html = TEMPLATE.read_text(encoding="utf-8")

    # ---- 1. drop every script block ------------------------------------
    html, n_scripts = re.subn(r"\n?<script\b.*?</script>\n?", "\n", html, flags=re.S)
    if n_scripts < 1:
        sys.exit("[FAIL] no <script> block found - template changed?")
    print(f"[OK]   removed {n_scripts} script block(s)")

    # ---- 1b. drop motion-only markup -----------------------------------
    html, n_motion = re.subn(
        r"\n?<!-- motion:start -->.*?<!-- motion:end -->\n?", "\n", html, flags=re.S
    )
    if n_motion != 2:
        sys.exit(f"[FAIL] expected 2 motion markup blocks, found {n_motion}")
    print(f"[OK]   removed {n_motion} motion markup block(s)")

    # ---- 1c. drop the motion CSS layer ---------------------------------
    html, n_css = re.subn(r"/\* motion:start \*/.*?/\* motion:end \*/\n", "", html, flags=re.S)
    if n_css != 1:
        sys.exit(f"[FAIL] expected 1 motion CSS block, found {n_css}")
    print("[OK]   removed motion CSS layer")

    # ---- 2. drop the JS-only hamburger --------------------------------
    html = sub_once(
        r"\n\s*<button class=\"menu-btn\"[^>]*>Menu</button>",
        "",
        html,
        "removed hamburger button",
    )

    # ---- 3. reveal: visible by default --------------------------------
    html = sub_once(
        r"/\* ---------- REVEAL ---------- \*/\n"
        r"/\* scoped to \.js so content is never invisible without JavaScript \*/\n"
        r"\.js \.reveal\{[^}]*\}\n"
        r"\.js \.reveal\.in\{[^}]*\}",
        "/* ---------- REVEAL ---------- */\n"
        "/* Canva build: no JS, so everything is visible by default */\n"
        ".reveal{opacity:1;transform:none}",
        html,
        "reveal starts visible",
    )

    # ---- 4. mobile nav: always rendered, wrapped row -------------------
    html = sub_once(
        r"  \.navlinks\{\n    position:absolute;[^}]*\}\n  \.navlinks\.open\{display:flex\}\n  \.navlinks a\{[^}]*\}\n  \.menu-btn\{display:block\}",
        "  .navlinks{position:static;flex-direction:row;flex-wrap:wrap;justify-content:center;\n"
        "    background:none;border:0;padding:0;display:flex;gap:.1rem}\n"
        "  .navlinks a{padding:.45rem .6rem;border-radius:10px;font-size:.86rem}\n"
        "  nav{height:auto;padding:.6rem 0;flex-wrap:wrap;gap:.4rem;justify-content:center}",
        html,
        "mobile nav always visible",
        re.S,
    )

    # ---- 5. caption styles --------------------------------------------
    html = sub_once(
        r"/\* ---------- REVEAL ---------- \*/",
        FIGCAPTION_CSS + "\n/* ---------- REVEAL ---------- */",
        html,
        "added figcaption styles",
    )

    # ---- 6. replace each JS gallery with two static figures -----------
    for key, spec in PROJECTS.items():
        # caption the main screenshot
        html = sub_once(
            rf'(<img id="{key}-main"[^>]*>)(\s*</figure>)',
            rf"\1\n              <figcaption>{spec['main_caption']}</figcaption>\2",
            html,
            f"{key}: captioned main figure",
        )
        # the thumbnail strip becomes a second full screenshot
        html = sub_once(
            rf'\n\s*<div class="thumbs" data-for="{key}-main">.*?</div>\n\s*</div>',
            "\n            <figure class=\"shot\">\n"
            f"              <img src=\"__IMG_{spec['second']}__\"\n"
            f"                   alt=\"{spec['second_caption']} screenshot\"\n"
            "                   width=\"1280\" height=\"889\">\n"
            f"              <figcaption>{spec['second_caption']}</figcaption>\n"
            "            </figure>\n"
            "          </div>",
            html,
            f"{key}: second screenshot as figure",
            re.S,
        )

    # ---- 7. inline each image exactly once ---------------------------
    for spec in PROJECTS.values():
        for name in (spec["main"], spec["second"]):
            jpg = IMAGES / f"{name}.jpg"
            if not jpg.exists():
                print(f"[FAIL] image not found: {jpg}")
                return 1
            placeholder = f"__IMG_{name}__"
            refs = html.count(placeholder)
            if refs != 1:
                print(f"[FAIL] {placeholder} referenced {refs} times, expected 1")
                return 1
            data = base64.b64encode(jpg.read_bytes()).decode("ascii")
            html = html.replace(placeholder, f"data:image/jpeg;base64,{data}")
            print(f"[OK]   inlined {name:16} {jpg.stat().st_size // 1024:4d} KB")

    # ---- 8. guard rails ----------------------------------------------
    problems = []
    if "<script" in html:
        problems.append("<script> still present")
    if "__IMG_" in html:
        problems.append("unreplaced placeholder")
    if "motion:start" in html or "motion:end" in html:
        problems.append("motion layer still present")
    if "preloader" in html:
        problems.append("preloader still present")
    if "cursor-aura" in html:
        problems.append("pointer aura still present")
    if "marquee-track" in html:
        problems.append("marquee still present")
    if ".js .reveal" in html:
        problems.append("JS-gated reveal rule still present")
    if re.search(r"\.reveal\{opacity:0", html):
        problems.append("reveal still hidden by default")
    if 'class="menu-btn"' in html:
        problems.append("hamburger button still present")
    if re.search(r"\.navlinks\{[^}]*display:none", html, re.S):
        problems.append("nav still hidden on small screens")
    if problems:
        for p in problems:
            print(f"[FAIL] {p}")
        return 1

    OUTPUT.write_text(html, encoding="utf-8")
    size = OUTPUT.stat().st_size / 1024
    print(f"\n[OK]   wrote {OUTPUT.name}  {size:.0f} KB  (no JS, 4 images)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
