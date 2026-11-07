# Afshin Hasani — Portfolio and Resume

Source for <https://iamafshiin.github.io> and the Resume PDF. Both are generated from one Content Source; nothing in `_site/` is edited by hand.

## Layout

```
cv.yaml                   Content Source: roles, skills, education (RenderCV format)
portfolio.yaml            Content Source: site-only data (hero, Proof Point cards, open source)
case-studies/<slug>.md    one Case Study each; frontmatter links it to a role
navy/                     RenderCV theme for the Resume (must sit next to cv.yaml)
site/templates/           Jinja2 templates: base, home, case-study, 404, sitemap
site/static/              favicon, robots.txt, css, js, self-hosted fonts
build.py                  cv.yaml + portfolio.yaml + case-studies -> _site/
checks.py                 Resume and site gate used by CI
```

## Build locally

```powershell
pip install -r requirements.txt
$env:PYTHONUTF8 = "1"
rendercv render cv.yaml
python build.py
python checks.py --site _site
python -m http.server 8080 -d _site
```

`checks.py` fails when:

- the Resume PDF is not exactly 2 pages, contains a phone number, or `pdftotext -raw`, `pdftotext -layout` or pypdf separate a date from its role, a skill label from its values or a degree from its date;
- a link, asset or anchor in `_site/` does not resolve;
- a Proof Point, role line, Case Study section or Role line is missing from the static HTML (pages must read fully without JS);
- CSS animates outside `@media (prefers-reduced-motion:no-preference)`;
- a Case Study names a company that is not a role in `cv.yaml`.

A phone-bearing Resume for direct applications is rendered locally only:

```powershell
rendercv render cv.yaml --cv.phone "+98 ..." --output-folder private_output
```

## Deploy

`.github/workflows/pages.yml` renders the Resume, builds the site, runs `checks.py` and deploys `_site/` to GitHub Pages (source: GitHub Actions). Pull requests build and check only; pushes to `main` deploy. A failed check leaves the last good deploy live.
