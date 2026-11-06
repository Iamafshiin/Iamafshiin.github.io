# Afshin Hasani — portfolio (rebuilt)

New version of <https://iamafshiin.github.io>. Plain HTML, CSS, and vanilla JS.
No framework, no CDN. The Resume PDF is built in CI from `cv.yaml`.

## Files

```
index.html                 the page
404.html                   GitHub Pages fallback page
favicon.svg                icon (hand-drawn monogram)
robots.txt                 crawl rules
sitemap.xml                one-page sitemap
assets/css/style.css       all styles
assets/js/main.js          small enhancements (~3 KB)
assets/fonts/*.woff2       self-hosted variable fonts (2 files, ~58 KB)
assets/og-image.png        1200x630 social preview image
assets/apple-touch-icon.png
```

## What changed, and why

**Speed**
- Removed the Tailwind CDN (a runtime compiler, ~100 KB+) and Chart.js (~200 KB). All styling is hand-written CSS, ~11 KB gzipped.
- Fonts are self-hosted (two variable `.woff2` files) and preloaded, instead of a blocking Google Fonts `@import`.
- Dropped the four Unsplash stock photos: external images, no dimensions set (layout shift), and generic enough to say nothing. The hero now uses a code/blueprint card instead.

**Bugs fixed**
- `.glass-card` had `border: 1px border rgba(...)` — invalid CSS, so the cards had no border at all.
- Every card started at `opacity: 0` and only appeared if JavaScript ran. Now content is visible by default; the reveal animation is a progressive enhancement with a safety timeout.
- No navigation at all on phones (the menu was `hidden md:flex`). Now there is a real menu button with `aria-expanded`, Escape to close, and focus handling.
- Copyright said 2024; it is now computed from the current year.

**SEO**
- Real `<title>` and meta description, canonical URL, Open Graph + Twitter card tags with a generated 1200×630 image.
- JSON-LD `Person` block (name, role, email, GitHub, skills).
- `robots.txt`, `sitemap.xml`, `404.html`, and an SVG favicon (the old site had none).
- Proper heading order, one `h1`, descriptive section labels.

**Accessibility**
- Skip link, `header`/`main`/`footer` landmarks, visible `:focus-visible` rings on every control.
- Contrast raised for small labels; `prefers-reduced-motion` and `prefers-contrast` respected.
- Links are real links; buttons are real buttons; the decorative pulse is `aria-hidden`.

**Content**
- Removed the "Tech Stack Utilization / Efficiency %" bar chart — invented numbers impress nobody.
- Each project now has a problem statement, two concrete bullets, and a stack row.
- Added an "Approach" section (three engineering rules) so the page says *how* you think, not only what you used.
- Added an "Open source" section built from the real public repos: `auth-microservice`, `message-microservice`, `SafeDriveRL`, `ram-monitoring-app`, plus GitHub and Stack Overflow links.
- Removed "no demos" claims and filler; contact section has a copy-email button.

## Resume

`cv.yaml` is the Content Source; the `navy/` folder is the RenderCV theme (RenderCV only finds a theme folder next to the YAML).

```powershell
pip install -r requirements.txt
$env:PYTHONUTF8 = "1"
rendercv render cv.yaml
python checks.py
```

`checks.py` fails unless the PDF is exactly 2 pages, `pdftotext -raw`, `pdftotext -layout` and pypdf keep every date with its role, every skill label with its values and every degree with its date, and no phone number is present.

For a phone-bearing copy for direct applications, render locally only:

```powershell
rendercv render cv.yaml --cv.phone "+98 ..." --output-folder private_output
```

## Deploy

GitHub Actions (`.github/workflows/pages.yml`) renders the Resume, runs `checks.py` and assembles `_site/` with the site files and `afshin-hasani-resume.pdf`. Pull requests build and check only; pushes to `main` deploy. A failed check leaves the last good deploy live. Repo setting: Pages → Source → GitHub Actions.

## Personalize before publishing

Search `index.html` for these and replace:

1. GitHub, LinkedIn, and Stack Overflow are already wired in (hero links, contact links, and the JSON-LD `sameAs`). If you add Telegram or X, put them next to those in both places.
2. The bullets under each project in `#work` — swap in your real numbers (latency, throughput, migration size). Right now they are rewritten from your existing descriptions, nothing invented.
3. The three figures in `.stats` (`6+`, `7,000+`, `50+`).
5. `sitemap.xml` — update `<lastmod>` after edits. Regenerate `assets/og-image.png` if your title changes.

## Local preview

Open `index.html` directly, or serve the folder:

```powershell
python -m http.server 8080
```
