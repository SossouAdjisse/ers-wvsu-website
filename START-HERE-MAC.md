# START HERE — ERS–WVSU website on your MacBook

This is the updated website package. **No paid WordPress hosting is needed**, and you do not need to purchase a domain until the GitHub preview meets your expectations.

## 1. Preview the complete site

1. Unzip `ERS-WVSU-Research-Website-v3.zip` and open the folder `ERS-WVSU-GitHub-Site`.
2. Double-click `Preview-on-Mac.command`. If macOS blocks it, right-click the file → **Open**, or open System Settings → Privacy & Security → **Open Anyway** for that specific file.
3. Your local browser opens to `http://127.0.0.1:8000/`.
4. Check **Home, Partnerships, Seminars, Past speakers, People, Students, Get involved, About**. Research resources are linked from the footer.
5. Stop the Terminal preview with **Control + C**.

To use Terminal without the `.command` file, open Terminal, type `cd ` (with a space), drag the **ERS-WVSU-GitHub-Site** folder into Terminal, press Return, then run:

```bash
python3 scripts/build.py --serve
```

You need Python 3. The included builder uses only Python's standard library. If Python is missing, obtain it from https://www.python.org/downloads/.

## 2. Create or prepare a GitHub repository

If you do **not yet have** a repository, create a **public** repository named `ers-wvsu` at https://github.com/new. Do not initialize it with a README, license or `.gitignore`. In Terminal, from the unzipped website folder, run:

```bash
git init
git branch -M main
git add .
git commit -m "Launch updated ERS-WVSU website"
git remote add origin https://github.com/YOUR_USERNAME/ers-wvsu.git
git push -u origin main
```

Replace `YOUR_USERNAME` with your real GitHub username. GitHub authentication may require a browser/credential manager or SSH; a GitHub account password alone is not accepted for HTTPS Git pushes.

**If you already have an `ers-wvsu` GitHub repository**, do not blindly `git init` or overwrite your version history. Open the existing local clone, copy the revised content and source files from this package (preserving `.github/` and `.pages.yml`), inspect the changes with `git diff`, and commit them on `main` when approved.

## 3. Activate free GitHub Pages

In the repository, open **Settings → Pages** and select **GitHub Actions** for the source. The included deployment workflow runs when you push to `main`. Your temporary public URL will normally be:

`https://YOUR_USERNAME.github.io/ers-wvsu/`

There is no Porkbun configuration yet.

## 4. Edit locally and decide when to publish

Edit the relevant JSON files using VS Code, Codex, or a text editor. Example changes:

- Bigger font / different background → `content/appearance.json`
- Homepage wording → `content/pages/home.json`
- Collaboration page → `content/pages/partnerships.json`
- Research topics → `content/themes.json`
- Future seminar → a verified JSON entry in `content/events/`
- Past speaker or faculty biography → `content/speakers/`
- Student Research & Mentorship page → `content/pages/students.json`
- Student project (permission required) → `content/student-projects/`
- Contact email → `content/site.json`

Preview and validate:

```bash
python3 scripts/build.py
python3 scripts/check_site.py
python3 scripts/build.py --serve
```

Push only after approval:

```bash
git add .
git commit -m "Refine ERS-WVSU website"
git push origin main
```

Only commits pushed to the publishing branch go live. **Do not commit confidential research even to another branch of a public repository.**

## 5. Optional editing from a browser

Visit https://app.pagescms.org/, sign in with GitHub and give the Pages CMS GitHub App access to this repository. The included `.pages.yml` enables editing of **Appearance**, all page copy, **Research themes**, **Research capabilities**, the collaboration process, seminar events, people, and archive resources. When saved on `main`, edits can publish automatically; use local Git for review-first publishing.

## 6. Professional domain later

When satisfied with the site, read `PORKBUN-DOMAIN-GUIDE.md`. You can use a new `.com` domain if available, or discuss an institution-owned WVSU subdomain with university IT. Domain registration and any university/brand approvals are separate from GitHub hosting.
