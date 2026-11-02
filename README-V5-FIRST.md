# ERS–WVSU — Version 5: Leadership, Research & Engagement

**Published website:** https://www.erswvsu.com/  
**Existing GitHub repository:** https://github.com/SossouAdjisse/ers-wvsu-website  
**Working copy:** `~/Projects/ers-wvsu-website` on the MacBook.

V5 is an UPDATE to the current website, not a new repository or domain. Use the **safe updater** to apply to your existing Git folder. Do **not** replace the `.git` directory or recopy an old ZIP into the active project.

## What's in V5

1. **People:** a balanced **Initiating & Coordination Team** with Lead Coordinator & Co-Initiator (Sossou) and Co-Coordinator & Co-Initiator (Hailou, Bandara). Includes a Research Affiliates & Collaborators section acknowledging Dr. Clinton Arnold, Dr. Michael Young, Jonathan Austin, and Austin O'Connor for seminar attendance/support. The other participation categories are *prospective pathways*, not populated offices.
2. **Past seminars:** two confirmed presentations with dates, times in West Virginia, and research summaries; they appear on Past Speakers, Seminars, and individual researcher pages. The research descriptions DO NOT assert causal findings.
3. **Research focus:** economics, data analysis, and causal inference as a contribution to interdisciplinary work. Research themes now include AI in agriculture, work, and education; no confidential project plans are disclosed.
4. **Design:** more readable type, two-row stable desktop header, mobile navigation menu, refined gold/charcoal/ivory palette, and muted gold accent bands halfway through broad dark sections. Adjustable through `content/appearance.json`.
5. **Online research inquiry:** Formspree integrated at `https://formspree.io/f/xjyypppg`. Visitors can submit on the website rather than opening their email app. The form uses topic selection, consent checkbox, honeypot, and accessible status messages; **one form recipient** is configured in Formspree (`contact@erswvsu.com`, which forwards to your WVSU inbox). Nine separate public email forwarding addresses remain available for direct correspondence.
6. **Mailing list:** an attractive, honest “coming soon” section is ready for Brevo. It **does not collect subscriptions yet**. Once you create a Brevo signup form and verify it, add its URL to `content/site.json` under `mailing_list_url`, build, and push.
7. **GitHub Pages:** existing Actions deployment and Porkbun DNS settings remain unchanged.

## Publish safely from your Mac

1. Unzip `ERS-WVSU-V5-Safe-Updater.zip` into Downloads.
2. Open Terminal and run:

```bash
python3 ~/Downloads/ERS-WVSU-V5-Update/Apply-ERS-V5.py
cd ~/Projects/ers-wvsu-website
python3 scripts/build.py
python3 scripts/check_site.py
git status --short
git add .
git commit -m "Upgrade ERS-WVSU to V5"
git push
```

3. Verify the latest workflow succeeds at the repository's **Actions** tab, then refresh https://www.erswvsu.com/.

The updater refuses to run with uncommitted changes and saves a ZIP backup under `~/Projects/ers-wvsu-backups/` before editing your repository. It preserves your `.git` folder, all existing domain and mailing-list settings, all nine ERS email addresses, and any custom presentation notes.

## Before public announcements

- **Review role titles with Hailou and Bandara**, and check the consent/accuracy of the four supporter listings.
- Check the two speaker summaries for any factual or editorial changes needed.
- **Send ONE real test submission** from the website after deployment. Check the Formspree dashboard and the WVSU inbox. The automated browser test simulated success/error; it did not transmit real data to Formspree.
- Do not describe proposed initiatives as approved funded projects. Do not publish sensitive preliminary research details or student projects without consent.
- Brevo signup is not live until the list is configured and tested. An independent approved donation route is not part of V5.

## Editing later

- Names, affiliations, role categories: `content/speakers/*.json`, `content/affiliates.json`, `content/community-roles.json`
- Past presentation details: `content/events/*.json` and speaker records
- Research themes: `content/themes.json`
- Typography / palette: `content/appearance.json` (via Pages CMS if enabled)
- Online form endpoint and newsletter URL: `content/site.json`
- Layout: `public/assets/css/site.css`; components: `scripts/build.py`

GitHub Pages hosts the static HTML and Formspree processes online submissions; no WordPress or paid hosting is required. Footer links to the WVSU website are for context and are not an official endorsement of any unapproved research partnership.
