"""Rebuild the portfolio and publish it to GitHub Pages.

One command for the whole loop:

    python tools/deploy.py            # rebuild + commit, then push
    python tools/deploy.py --no-push  # rebuild + commit only

Steps
-----
1. Rebuild the single-file portfolio from the template + screenshots.
2. Copy it to ``site/index.html`` — GitHub Pages serves whatever ``index.html``
   sits at the root of the repo, so that file is the live site.
3. Commit, if anything actually changed.
4. Push to the configured GitHub remote, if there is one.

You still have to create the empty GitHub repo once (GitHub no longer lets git
create it), and turn Pages on in Settings -> Pages.  After that this script
keeps the live site in sync with every edit.
"""

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BUILT = ROOT / "Christian-Jade-Badua-Portfolio.html"
SITE = ROOT / "site"
INDEX = SITE / "index.html"


def run(cmd, cwd=None, capture=False):
    """Run a shell command.

    ``capture=True`` swallows stdout so we can read it (returns text);
    otherwise the child's output goes straight to the terminal and we get None.
    """
    done = subprocess.run(
        cmd,
        cwd=cwd or ROOT,
        shell=True,
        text=True,
        stdout=subprocess.PIPE if capture else None,
    )
    return done.stdout if capture else done.returncode


def say(msg):
    print(msg, flush=True)


def main() -> int:
    push = "--no-push" not in sys.argv

    # 1. rebuild
    say("==> rebuilding portfolio")
    if run(f'"{sys.executable}" "{ROOT / "tools" / "build_portfolio.py"}"') != 0:
        say("[FAIL] build failed - not touching site/")
        return 1

    # 2. stage into the site folder
    SITE.mkdir(exist_ok=True)
    (SITE / ".nojekyll").touch()
    if not BUILT.exists():
        print(f"[FAIL] built file missing: {BUILT}")
        return 1
    shutil.copy2(BUILT, INDEX)
    size = INDEX.stat().st_size / 1024 / 1024
    say(f"==> site/index.html  {size:.2f} MB")

    # 3. commit
    say("==> committing")
    run("git add -A", cwd=SITE)
    if run('git diff --cached --quiet', cwd=SITE) == 0:
        say("    nothing changed - already up to date")
    else:
        if run('git commit -m "Update portfolio"', cwd=SITE) != 0:
            say("[FAIL] commit failed")
            return 1

    # 4. push
    remote = (run("git remote", cwd=SITE, capture=True) or "").split()
    if not push:
        say("==> --no-push given, stopping here")
        say(f"    review, then run:  git -C \"{SITE}\" push -u origin main")
        return 0
    if not remote:
        say("")
        say("[STOP] no GitHub remote configured yet.")
        say("  1. Create an EMPTY public repo on github.com (no README).")
        say("  2. In that repo: Settings -> Pages -> Source: Deploy from a")
        say("     branch, branch 'main', folder '/ (root)' -> Save.")
        say("  3. Then run these two commands:")
        say(f'     git -C "{SITE}" remote add origin <your-repo-url>')
        say(f'     git -C "{SITE}" push -u origin main')
        say("")
        say("  Your site goes live at https://cjadebadua117-sys.github.io/")
        say("  (allow a minute or two for the first build)")
        return 0

    say(f"==> pushing to {remote[0]}")
    if run("git push -u origin main", cwd=SITE) != 0:
        say("[FAIL] push failed")
        return 1
    say("")
    say("[OK] pushed. GitHub Pages rebuilds in about a minute.")
    return 0


if __name__ == "__main__":
    sys.exit(main())