# Afshin Hasani — Portfolio and Resume

Source for <https://iamafshiin.github.io> and the Resume PDF. Both are generated from one Content Source; nothing in `_site/` is edited by hand.

## Layout

```
cv.yaml                   Content Source: roles, skills, education (RenderCV format)
portfolio.yaml            Content Source: site-only data, in plain language (hero, explainer, project cards, wins)
case-studies/<slug>.md    one Case Study each: plain-language story + a collapsed "Technical details" section
fa/portfolio.yaml         Persian (RTL) version of portfolio.yaml, served at /fa/
fa/case-studies/<slug>.md Persian Case Studies; same slugs, Technical details kept in English
navy/                     RenderCV theme for the Resume (must sit next to cv.yaml)
site/templates/           Jinja2 templates: base, home, case-study, 404, sitemap
site/static/              favicon, robots.txt, css, js, self-hosted fonts
build.py                  cv.yaml + portfolio.yaml + case-studies -> _site/
checks.py                 Resume and site gate used by CI
```

## Writing style

The site is written for people who are not engineers (recruiters, founders, friends). Keep the main text free of jargon; put engineering detail under `## Technical details` in each Case Study, which renders as a closed section. Projects with an `image` show a product image cropped from the company's own website (`site/static/assets/work/`), captioned with its source; the others fall back to the drawings in `site/templates/_mockup.html.j2`, which are labelled as drawings. All page text, including button labels and the phone screens, lives under `ui:` in each `portfolio.yaml`, so English and Persian share the same templates.

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
- a project card, role line, Case Study section, summary, step or Role line is missing from the static HTML;
- CSS animates outside `@media (prefers-reduced-motion:no-preference)`;
- a Case Study names a company that is not a role in `cv.yaml`.

A phone-bearing Resume for direct applications is rendered locally only:

```powershell
rendercv render cv.yaml --cv.phone "+98 ..." --output-folder private_output
```

## Deploy

`.github/workflows/pages.yml` renders the Resume, builds the site, runs `checks.py` and deploys `_site/` to GitHub Pages (source: GitHub Actions). Pull requests build and check only; pushes to `main` deploy. A failed check leaves the last good deploy live.
