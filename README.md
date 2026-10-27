# Portfolio — Christian Jade Badua

> **23 Oct 2026 — new animated design.** The portfolio now uses the
> [ArsalanKaleem/portfolio](https://github.com/ArsalanKaleem/portfolio)
> template (MIT), rebuilt with Christian's content and screenshots. Edit
> `Christian-Jade-Badua-Portfolio.html` (or `site/index.html`) directly.
> Running `tools/build_portfolio.py` rebuilds the **older** design from
> `portfolio_assets/portfolio.template.html`, so don't run it unless you
> want to go back.

## Viewing it

**`Christian-Jade-Badua-Portfolio.html`** — one self-contained file, 1.02 MB.

Double-click it to open in your browser. There is no server to start and no
command to run: CSS, JavaScript, the animation libraries and all four
screenshots are embedded in the file. The only external reference is Google
Fonts, so it also renders offline (it falls back to a system font when
disconnected).

## Live on the internet

**Published:** https://cjadebadua117-sys.github.io/

Served by GitHub Pages from the public repo
`cjadebadua117-sys/cjadebadua117-sys.github.io` (branch `main`, `/` root). It
stays online whether this laptop is on or not.

**Every edit:**

```
python tools/deploy.py
```

rebuilds, copies into `site/`, commits and pushes. GitHub Pages rebuilds in
about a minute.

**One-time setup is already done** (`publish.py` ran on 23 Oct 2026 and created
the repo, pushed `site/` and enabled Pages). You only need it again if the repo
is ever deleted:

```
gh auth login --hostname github.com --git-protocol https --web
python tools/publish.py
```

It publishes at the bare root — `https://cjadebadua117-sys.github.io/` — rather
than burying it under a `/portfolio/` path.

<details>
<summary>Doing it by hand instead (no GitHub CLI)</summary>

1. On github.com create an **empty public repo** (tick Public, untick
   "Add a README") — GitHub no longer lets `git push` create the repo for you.
2. In that repo: **Settings -> Pages**, Source *Deploy from a branch*, branch
   `main`, folder `/ (root)`, Save.
3. `git -C site remote add origin <repo-url>` then `git -C site push -u origin main`.

</details>

---

## If you want to edit it

**Edit `portfolio_assets/portfolio.template.html` — never the built file.**
The built `.html` has ~400 KB of base64 image data glued into it, which makes
hand-editing painful and easy to break.

The template refers to screenshots as placeholders:

```html
__IMG_bhims-landing__
__IMG_bhims-listings__
__IMG_cis-dashboard__
__IMG_cis-home__
```

After saving the template, regenerate the single file:

```
python tools/build_portfolio.py     # just rebuild
python tools/deploy.py              # rebuild + update site/ + commit (+ push)
```

The script reads the four JPGs from `portfolio_assets/opt/`, replaces each
placeholder with the matching image as a base64 data URI, and overwrites
`Christian-Jade-Badua-Portfolio.html`. It needs no packages — standard library
only, so plain `python` on your PATH works.

---

## The animation layer

The whole page is animated with **GSAP 3.15 + ScrollTrigger + SplitText** and
**Lenis** smooth scrolling. All four libraries are vendored into
`portfolio_assets/vendor/` and inlined by the build, so the file still works
with no internet connection.

What moves:

| Where | What happens |
|---|---|
| Page load | Preloader counts 0→100, then wipes upward to reveal the hero |
| Hero | Headline splits into words and rises; lede, buttons and stats follow; stat numbers count up from zero |
| Hero (desktop) | Section pins for ~0.85 of a screen; headline scales/fades, lede and stats drift out |
| Header | Slides away while reading down, returns on scroll up |
| Sections | `.reveal` blocks fade and rise on entry, staggered in batches |
| Project screenshots | Image un-clips as it enters (clip-path scrub) and parallaxes inside its frame; hover scales it |
| Section headings | Split into lines and masked, then revealed line by line |
| Stack cards | Cascade in with a slight rotation offset |
| End of work | Infinite tech marquee band (pauses on hover) |
| Buttons | Magnetic — they lean toward the pointer |
| Pointer | Soft aura ring that grows over links (native cursor stays visible) |
| Top edge | Thin gradient progress bar tied to scroll position |

**Guard rails.** Nothing depends on the motion to be readable:

- Every hidden state is scoped to `.js`, and the class is set by a one-line
  head script. With JavaScript off — or in the Canva build, which strips it —
  the page renders fully visible.
- `prefers-reduced-motion: reduce` skips the animation code entirely and
  disables the pin and marquee.
- If the motion code throws, a catch block removes the preloader and reveals
  every section; an 8-second failsafe does the same if the intro ever stalls.
- The pinned hero only activates at `min-width:900px` **and**
  `min-height:700px`, so short laptop windows and phones scroll normally.

**Tuning it.** Durations, stagger and easing all live in the final `<script>` of
the template. The CSS layer is wrapped in `/* motion:start */` …
`/* motion:end */`, and motion-only markup in `<!-- motion:start -->` …
`<!-- motion:end -->` — `build_canva.py` deletes both, which is why the Canva
twin has no dead scroll space and no preloader.

---

## Importing into Canva

Canva Code 2.0 (July 2026) can import a standalone `.html` file, but its help
page lists three things that do not survive: **JavaScript is not supported on
imported designs**, complex CSS may not convert exactly, and very large files
may take a long time to process.

The main file is a poor fit for that importer — 98% of it is base64 image data
(1.54 MB), it carries four inlined animation libraries plus an application
script, and its layout is tuned for scroll-driven motion (a pinned hero would
leave a screen of empty scroll behind once the JavaScript is gone).

So there is a second, static build made for that import:

```
python tools/build_canva.py     ->  Christian-Jade-Badua-Portfolio-Canva.html
```

It derives from the same template, so nothing is edited twice, and it differs
only in the ways Canva forces:

| | Main file | Canva build |
|---|---|---|
| JavaScript | 6 `<script>` blocks (GSAP, ScrollTrigger, SplitText, Lenis + app) | none |
| Motion | full scroll animation | none |
| Content visible without JS | yes (progressive enhancement) | yes |
| Screenshots | 4 images, 10 references | 4 images, one each, captioned |
| Gallery / mobile menu | clickable / hamburger | static figures / always-visible nav |
| Size | 1.54 MB | 558 KB |

To import: in Canva, **Uploads -> upload the `.html`** (or drag it onto the
home page). It opens as an editable Code design; publish it from the Code
window with **Publish**. Free accounts get a `Made in Canva` badge and a
`canva.site` address; a custom domain needs a paid plan.

The GitHub Pages site stays the primary portfolio — the Canva copy is a static
twin, so any content edit has to be built and imported again.

---

## Folder layout

```
Portfolio/
├── Christian-Jade-Badua-Portfolio.html   <- the deliverable (generated)
├── Christian-Jade-Badua-Portfolio-Canva.html  <- static twin for Canva import (generated)
├── README.md
├── portfolio_assets/
│   ├── portfolio.template.html           <- EDIT THIS
│   ├── opt/*.jpg                         <- optimised shots the build inlines
│   ├── vendor/*.js                       <- GSAP, ScrollTrigger, SplitText, Lenis
│   ├── *.png                             <- original full-size captures
│   └── _pages/*.html                     <- captured pages (build intermediates)
├── site/                                 <- git repo that becomes the live site
│   ├── index.html                        <- generated from the file above
│   └── .nojekyll                         <- stops GitHub Pages running Jekyll
└── tools/
    ├── build_portfolio.py                <- template + images -> single file
    ├── build_canva.py                    <- static twin for Canva's HTML import
    ├── publish.py                        <- ONE-TIME: create repo + push + enable Pages
    ├── deploy.py                         <- every edit after: rebuild + commit + push
    └── capture_portfolio.py              <- re-shoot screenshots from the live apps
```

---

## Re-taking the screenshots

`tools/capture_portfolio.py` logs into both systems and saves the rendered
HTML so Chrome can photograph them. It only works while the apps are running:

| System | Folder | Port | Command |
|---|---|---|---|
| CIS-Prox | `Desktop/Cis-proximity` | `8000` | `python manage.py runserver 127.0.0.1:8000` |
| BHIMS | `Desktop/BOARDING HOUSE INFO MANAGEMENT SYSTEMS` | `8001` | `python manage.py runserver 127.0.0.1:8001` |

The CIS-Prox dashboard shot logs in as `testdavao` / `Secret123` — that demo
account only exists in your local database, so change the credentials at the
top of the script if you reset it.

This folder is fully self-contained: it shares no files and no virtual
environment with either Django project.

---

## The two systems featured

**BHIMS** (primary) — Boarding House Information Management System, built for
DMMMSU–NLUC. Django 6.0 · MySQL/XAMPP · Bootstrap 5. 14 models, 92 view
functions, 73 tests, 4 architecture diagrams.

**CIS-Prox** (second) — Student Presence & Real-Time Locating System.
Django 5.2 · MySQL/XAMPP. 22 tables, 27 templates, 19 migrations.