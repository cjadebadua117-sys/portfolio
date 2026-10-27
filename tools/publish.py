"""One-time bootstrap: publish the portfolio to GitHub Pages.

Run this ONCE. It creates the public GitHub repo, pushes ``site/`` and turns on
GitHub Pages.  After that, use ``tools/deploy.py`` for routine updates.

    python tools/publish.py

Requires being signed in first:

    gh auth login

Repo name is the GitHub *user site* form (``<login>.github.io``), which publishes
at the bare root URL -- https://cjadebadua117-sys.github.io/ -- rather than
burying it under a ``/portfolio/`` path.
"""

import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"

# gh is installed portable (no admin needed), so it is not on PATH by default
GH_CANDIDATES = [
    shutil.which("gh"),
    r"C:\Users\Admin\AppData\Local\gh-portable\bin\gh.exe",
]


def find_gh():
    for c in GH_CANDIDATES:
        if c and Path(c).exists():
            return c
    sys.exit("[FAIL] gh not found. Install GitHub CLI, or run: gh auth login")


def gh(*args, capture=True):
    cmd = [GH, *args]
    print("  $ gh", " ".join(args), flush=True)
    r = subprocess.run(cmd, text=True, stdout=subprocess.PIPE if capture else None)
    return r


def say(m):
    print(m, flush=True)


def main() -> int:
    global GH
    GH = find_gh()
    say(f"using gh at {GH}")

    # 1. auth
    who = subprocess.run([GH, "api", "user", "--jq", ".login"],
                         text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if who.returncode:
        say("")
        say("[STOP] not signed in to GitHub. Run this first, in your terminal:")
        say("")
        say('    "%s" auth login --hostname github.com --git-protocol https --web' % GH)
        say("")
        say("It prints a one-time code; approve it in the browser. Re-run this")
        say("script afterwards and it will publish everything.")
        return 1

    login = who.stdout.strip()
    say(f"[OK] signed in as {login}")

    repo_name = f"{login}.github.io"
    say(f"[OK] target repo: {repo_name}  ->  https://{repo_name}/")

    # 2. create + push
    say("")
    say("==> creating the public repo and pushing site/")
    exists = subprocess.run([GH, "repo", "view", repo_name],
                            text=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if exists.returncode == 0:
        say(f"    repo already exists - pushing to it instead")
        if subprocess.run(["git", "remote", "get-url", "origin"],
                          cwd=SITE, text=True,
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode:
            subprocess.run(["git", "remote", "add", "origin",
                            f"https://github.com/{login}/{repo_name}.git"], cwd=SITE)
        if subprocess.run(["git", "push", "-u", "origin", "main"],
                          cwd=SITE).returncode:
            say("[FAIL] push failed")
            return 1
    else:
        if subprocess.run([GH, "repo", "create", repo_name,
                           "--public", "--source", str(SITE), "--push"],
                          capture=False).returncode:
            say("[FAIL] repo creation failed")
            return 1

    # 3. enable Pages
    say("")
    say("==> enabling GitHub Pages")
    r = subprocess.run([GH, "api", "--method", "POST",
                        f"repos/{login}/{repo_name}/pages",
                        "-f", "source[branch]=main",
                        "-f", "source[path]=/"],
                       text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if r.returncode:
        # 409/422 just means it is already enabled
        if "already" in (r.stderr or "").lower():
            say("    already enabled")
        else:
            say(f"    [warn] {(r.stderr or '').strip()[:200]}")
            say("    enable it manually: Settings -> Pages -> branch main, / (root)")
    else:
        say("    Pages enabled")

    # 4. report
    say("")
    say(f"[OK] published -> https://{repo_name}/")
    say("    first build takes 1-2 minutes")
    return 0


if __name__ == "__main__":
    sys.exit(main())