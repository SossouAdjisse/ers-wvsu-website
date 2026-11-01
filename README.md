# ERS–WVSU | Research-to-Evidence Website

**Economic Research Seminar at West Virginia State University**

This is the upgraded, complete **economics-centered academic website** for the ERS–WVSU research initiative. It is designed for **GitHub Pages (free static hosting)**, with **Porkbun (optional domain registration)** and **Pages CMS (optional browser-based editing)**. It uses Python 3 and standard library only—no paid hosting, Node modules, or database.

**Read `START-HERE-MAC.md` first**, especially if this is your first GitHub site.

## Positioning

ERS–WVSU is **not a general interdisciplinary lecture series**. It invites economists and researchers from other disciplines when their work can benefit substantively from **economic framing, econometrics and data analysis, causal inference, or collaborative research development**. Speakers do not need an economics component in advance; discovering and building it may be the research contribution.

The site publicly describes broad **research themes**, not confidential proposals, the three private project concepts discussed during planning, or supposed institutional partnerships. See `EDITORIAL-AND-RESEARCH-SCOPE.md`.

## Pages

| Website section | Purpose |
| --- | --- |
| **Home** | Why ERS exists, methods-oriented value proposition, broad research themes, seminar introduction |
| **Research partnerships** | Six capabilities, four-step collaboration process, presentation selection principles, campus research context |
| **Seminars** | Verified upcoming and completed seminars, seminar details and optional calendar downloads |
| **Past speakers** | Previous ERS–WVSU presenters and their research topics |
| **People** | Searchable faculty profiles, including Sossou S. Adjisse, Frehot Hailou, and Saman Bandara |
| **Student Research & Mentorship** | Student Research Spotlight, research development pathways, and potential mentoring opportunities |
| **Resources** | Approved public presentation slides, research briefs, and other research materials |
| **Get involved** | Research proposal criteria and a visitor-completed email-draft inquiry form (Google Forms link can be added) |
| **About** | Refined mission, interdisciplinary scope, standards, history, and collaboration principles |

## What you can edit without rewriting the website

- **Fonts and backgrounds:** `content/appearance.json` or Pages CMS → **Appearance: fonts & colors**. The site builds its theme stylesheet automatically.
- **All webpage wording:** `content/pages/*.json` or corresponding Pages CMS editor.
- **Broad research themes:** `content/themes.json`.
- **Research capabilities:** `content/capabilities.json`.
- **Four collaboration steps:** `content/pathway.json`.
- **Dates and speakers:** add approved entries to `content/events/*.json` and `content/speakers/*.json`.
- **Public archive:** `content/resources/*.json`.
- **Previous presenters:** in `content/speakers/*.json`, set `past_speaker: true`, with `past_talk` and `past_talk_note`.
- **Student spotlight:** new `content/student-projects/*.json` records with publication permission confirmed.
- **Advanced spacing, layouts and interaction:** `public/assets/css/site.css`, `scripts/build.py`, and `public/assets/js/site.js`.

### Three useful commands on your Mac

```bash
python3 scripts/build.py          # Build into dist/
python3 scripts/check_site.py     # Check links and structure
python3 scripts/build.py --serve  # Preview at http://127.0.0.1:8000/
```

You may also double-click `Preview-on-Mac.command`. If macOS blocks it, use **right-click → Open** or follow the system privacy prompts.

### Publish only after you approve your changes

```bash
git add .
git commit -m "Update ERS-WVSU website"
git push origin main
```

Pushing `main` triggers the included `.github/workflows/deploy.yml`, which builds and publishes `dist/`. Pages CMS saves edits to GitHub directly; changes to the live branch may publish immediately. For deliberate review before publication, edit locally and push only when ready.

## Project contents

```text
.github/workflows/deploy.yml    Automatic GitHub Pages build/deploy
.pages.yml                    Pages CMS editing configuration
content/appearance.json        Font sizes + background/accent colors
content/pages/*.json           Editable page wording, including partnerships
content/themes.json            Public illustrative research themes
content/capabilities.json      Research capabilities (not projects)
content/pathway.json           Four-step collaboration process
content/events/               Confirmed seminar records only
content/speakers/              Editable faculty profiles and past-presenter fields
content/student-projects/      Permission-controlled Student Research Spotlight records
content/resources/             Approved public research archive entries
content/site.json              Contact, domain, organization metadata
public/assets/css/site.css     Core visual design and responsive layout
public/assets/images/         Original, program-neutral SVG illustrations
public/assets/js/site.js       Menu and search functionality
public/media/                  Approved images and documents
scripts/build.py              No-dependency Python generator
scripts/check_site.py         Automated structure and link validation
Preview-on-Mac.command         Double-click local preview on Mac
```

`dist/` is included for preview convenience but excluded from version control. The GitHub workflow generates it afresh. **Do not upload confidential manuscripts, research datasets, unpublished proposal ideas, or sensitive materials to this public repository, even as 'draft' files.**

## Before publication

Review `BEFORE-YOU-PUBLISH.md` and `EDITORIAL-AND-RESEARCH-SCOPE.md`. The site intentionally has **no invented scheduled events or claimed external collaborations**. The inquiry form opens a visitor-generated email draft; it does **not** automatically submit a message. See `WHAT-CHANGED-V3.md`. The E.R.S. text mark and original graphics are *provisional*—institutional review of official name, brand and logo is recommended. University affiliation should not be mistaken for a formally authorized or exclusive campus research office.

## Useful documentation

- [GitHub Pages setup](https://docs.github.com/en/pages/getting-started-with-github-pages/creating-a-github-pages-site)
- [GitHub Pages via Actions](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site)
- [Pages CMS configuration](https://pagescms.org/docs/configuration/)
- [Pages CMS quick start](https://pagescms.org/docs/quick-start/)
- [WVSU official branding guidance](https://wvstateu.edu/wp-content/uploads/getattachment/5b/2019_graphicManual-1.pdf)
