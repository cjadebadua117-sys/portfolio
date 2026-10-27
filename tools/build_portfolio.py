"""Build the single-file portfolio.

The editable source is ``portfolio_assets/portfolio.template.html``; it refers
to screenshots with ``__IMG_<name>__`` placeholders and to the animation
libraries with ``/*__VENDOR_<name>__*/`` markers.  This script inlines both, so
the output is one self-contained file that still works with no network: open
it, email it, or push it to GitHub Pages.

Usage:
    python tools/build_portfolio.py
"""

import base64
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = ROOT / "portfolio_assets" / "portfolio.template.html"
IMAGES = ROOT / "portfolio_assets" / "opt"
VENDOR = ROOT / "portfolio_assets" / "vendor"
OUTPUT = ROOT / "Christian-Jade-Badua-Portfolio.html"

# order matters only for the report; each is looked up by name
NAMES = ["bhims-landing", "bhims-listings", "cis-dashboard", "cis-home"]

# marker in the template -> file that gets pasted in its place
LIBS = {
    "GSAP": "gsap.min.js",
    "SCROLLTRIGGER": "ScrollTrigger.min.js",
    "SPLITTEXT": "SplitText.min.js",
    "LENIS": "lenis.min.js",
}


def inline_libs(html: str) -> str:
    for key, filename in LIBS.items():
        js = VENDOR / filename
        if not js.exists():
            sys.exit(f"[FAIL] vendor file missing: {js}")
        src = js.read_text(encoding="utf-8")

        # A literal </script> inside the source would close the tag early.
        # Escaping the slash is safe in JS strings and comments.
        guard = src.lower().count("</script")
        if guard:
            src = src.replace("</script", "<\\/script")
            src = src.replace("</SCRIPT", "<\\/SCRIPT")

        marker = f"/*__VENDOR_{key}__*/"
        refs = html.count(marker)
        if refs != 1:
            sys.exit(f"[FAIL] expected 1 marker {marker}, found {refs}")
        html = html.replace(marker, src)
        print(
            f"[OK]   vendored {key:15} {js.stat().st_size // 1024:4d} KB"
            + (f"  ({guard} </script> escaped)" if guard else "")
        )
    return html


def main() -> int:
    if not TEMPLATE.exists():
        print(f"[FAIL] template not found: {TEMPLATE}")
        return 1

    html = TEMPLATE.read_text(encoding="utf-8")

    for name in NAMES:
        jpg = IMAGES / f"{name}.jpg"
        if not jpg.exists():
            print(f"[FAIL] image not found: {jpg}")
            return 1
        placeholder = f"__IMG_{name}__"
        refs = html.count(placeholder)
        if refs == 0:
            print(f"[FAIL] placeholder not in template: {placeholder}")
            return 1
        data = base64.b64encode(jpg.read_bytes()).decode("ascii")
        html = html.replace(placeholder, f"data:image/jpeg;base64,{data}")
        print(f"[OK]   {name:16} {jpg.stat().st_size // 1024:4d} KB  x{refs} refs")

    html = inline_libs(html)

    if "__IMG_" in html:
        print("[FAIL] unreplaced placeholder remains")
        return 1
    if "__VENDOR_" in html:
        print("[FAIL] unreplaced vendor marker remains")
        return 1

    OUTPUT.write_text(html, encoding="utf-8")
    print(f"\n[OK]   wrote {OUTPUT.name}  {OUTPUT.stat().st_size / 1024 / 1024:.2f} MB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
