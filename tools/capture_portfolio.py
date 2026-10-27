"""Capture portfolio screenshots of both campus systems.

How it works
------------
``requests`` is not a dependency of either project, so we use the stdlib.
For every target we log in with a cookie jar, fetch the rendered HTML, and
inject a ``<base href>`` tag pointing at the live dev server.  The saved HTML
is then served over HTTP (not file://) so relative asset URLs such as
``/static/style.css`` resolve back to the running app and Chrome renders the
page exactly as a logged-in browser would.

Usage:
    python tools/capture_portfolio.py
"""

import html
import http.cookiejar
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "portfolio_assets" / "_pages"
WINDOW = "1440,1000"

# name, base_url, path, login tuple or None
TARGETS = [
    ("cis-home", "http://127.0.0.1:8000", "/", None),
    ("cis-dashboard", "http://127.0.0.1:8000", "/dashboard/",
     ("testdavao", "Secret123")),
    ("bhims-landing", "http://127.0.0.1:8001", "/", None),
    ("bhims-listings", "http://127.0.0.1:8001", "/listings/", None),
]


def opener(base):
    jar = http.cookiejar.CookieJar()
    return urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar)), jar


def get(opener_obj, url, data=None):
    body = urllib.parse.urlencode(data).encode() if data else None
    req = urllib.request.Request(
        url,
        data=body,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) PortfolioCapture/1.0",
            "Content-Type": "application/x-www-form-urlencoded",
        },
    )
    with opener_obj.open(req, timeout=30) as resp:
        return resp.read().decode(resp.headers.get_content_charset() or "utf-8", "replace")


def cookie_value(jar, name):
    for c in jar:
        if c.name == name:
            return c.value
    return ""


def login(opener_obj, jar, base, username, password):
    get(opener_obj, base + "/login/")
    token = cookie_value(jar, "csrftoken")
    get(opener_obj, base + "/login/", {
        "csrfmiddlewaretoken": token,
        "username": username,
        "password": password,
    })


def with_base_tag(document, base):
    """Point every relative URL at the live dev server."""
    tag = '<base href="%s/">' % html.escape(base, quote=True)
    if re.search(r"<head[^>]*>", document, re.I):
        return re.sub(r"(<head[^>]*>)", r"\1" + tag, document, count=1, flags=re.I)
    return document.replace("<html>", "<html>" + tag, 1)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    made = []
    for name, base, path, creds in TARGETS:
        op, jar = opener(base)
        try:
            if creds:
                login(op, jar, base, *creds)
            page = get(op, base + path)
        except Exception as exc:  # keep going so one failure doesn't kill the run
            print(f"[FAIL] {name}: {exc}")
            continue
        (OUT / f"{name}.html").write_text(with_base_tag(page, base), encoding="utf-8")
        print(f"[OK]   {name}  ({len(page):,} bytes) -> {OUT / (name + '.html')}")
        made.append(name)
    print("\nCaptured:", ", ".join(made) or "none")
    return 0 if made else 1


if __name__ == "__main__":
    sys.exit(main())
