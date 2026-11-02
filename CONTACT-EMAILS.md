# ERS–WVSU contact addresses — publication and editing guide

The public site uses these nine addresses:

| Address | Intended use |
|---|---|
| contact@erswvsu.com | General inquiries |
| seminars@erswvsu.com | Seminar proposals and schedules |
| speakers@erswvsu.com | Speaker invitations and past-speaker records |
| partnerships@erswvsu.com | Interdisciplinary research partnerships |
| research@erswvsu.com | Economics, data analysis, and causal inference |
| grants@erswvsu.com | Funding proposals and grants |
| students@erswvsu.com | Student research submissions and spotlight |
| mentorship@erswvsu.com | Student and faculty research mentoring |
| outreach@erswvsu.com | Community and institutional outreach |

## IMPORTANT: Verify forwarding before promoting the new addresses

**This website cannot create mailboxes or configure Porkbun.** In Porkbun, create each
forward and have it deliver to `sossou.adjisse@wvstateu.edu` as you planned. Send a
test email from another account to each of the nine addresses and confirm arrival
and the ability to reply from WVSU. Free forwarding does not send mail as the
`@erswvsu.com` address; your reply will identify the WVSU sender.

## Where the website uses the addresses

- Get Involved: all nine in a contact directory; inquiry form routes a **draft**
  to the address corresponding to the selected topic.
- Research Partnerships: `partnerships`, `research`, `grants`.
- Seminars: `seminars`, `speakers`.
- Past Speakers and People: `speakers`.
- Student Research & Mentorship: `students`, `mentorship`.
- Research Archive: `research`.
- About: `contact`, `outreach`.
- Footer (on every page): `contact`, `seminars`, `partnerships`.

## Editing an email address in the future

Edit `content/site.json` (or in Pages CMS → Site settings). If you change an
address, also change its forwarding rule in Porkbun, then rebuild and push.
Do not store your actual mailbox password or login credentials in GitHub.

The research inquiry form is not a hosted form. It prepares an email in the
visitor's email application. They must review it and press **Send**. The static
website does not record inquiry contents.

## Build and publish

```bash
cd ~/Projects/ers-wvsu-website
python3 scripts/build.py
python3 scripts/check_site.py
git add content/site.json content/pages/get-involved.json .pages.yml scripts/build.py public/assets/js/site.js public/assets/css/site.css CONTACT-EMAILS.md
git commit -m "Add ERS-WVSU contact directory and inquiry routing"
git push
```
