# ERS–WVSU editing guide

**Control belongs to you.** Work locally on your Mac, test, then push—or use Pages CMS for routine edits. The site will stay available on GitHub Pages while you work locally.

## Change typography and backgrounds (no CSS expertise required)

Open **`content/appearance.json`** or **Pages CMS → Appearance: fonts & colors**.

| Setting | Initial value | Purpose |
| --- | --- | --- |
| `body_font_px` | 18 | Regular paragraphs and extended descriptions |
| `navigation_font_px` | 15 | Desktop and mobile menu links |
| `card_font_px` | 16 | Research, service, and process cards |
| `small_label_font_px` | 12 | Eyebrows and compact metadata |
| `background_color` | `#FCFBF7` | Main light background |
| `secondary_background_color` | `#F3F0E7` | Alternate sections |
| `dark_background_color` | `#151A17` | Hero, dark panels and footer |
| `accent_color` | `#CFAB2B` | Gold accent |

Font values are numbers (not strings like `"18px"`); color values must be six-digit hex colors. The website builder checks the values and generates `dist/assets/css/appearance.css`. **Do not edit that generated file; edit the JSON instead.** Font sizes are restricted to reasonable ranges to protect mobile layouts.

The default font families are set in `public/assets/css/site.css`. For further control of heading sizes, whitespace, images, or layout, edit that stylesheet. The E.R.S. text mark is provisional pending institutional branding review.

## Change the research scope and public messaging

- `content/pages/home.json` — value proposition, examples of contribution, call to action.
- `content/pages/partnerships.json` — partnership purpose, selection criteria, campus context.
- `content/capabilities.json` — public expertise cards (six initially).
- `content/pathway.json` — four-step collaboration process.
- `content/themes.json` — broad potential research areas, *not specific projects*.
- `content/pages/seminars.json` — format and selection explanation.
- Other `content/pages/*.json` — individual page descriptions.

**Never publish the three unannounced project concepts or other proprietary research proposals** as public “example projects.” If you later receive permission to name a confirmed collaboration, add it through an approved event or resource entry.

## Add a verified seminar

Pages CMS → **Seminar events → New**, or add a JSON file in `content/events/` containing real details. A seminar appears on the live site when status is `scheduled` or `completed`; `scheduled` events dated today or later appear in Upcoming, and completed events in Past. If start and end times are provided, the builder creates an `.ics` calendar file. All times are interpreted as local Eastern time (for this project, `America/New_York`).

Example structure **for reference only**—do not publish fake details:

```json
{
  "title": "VERIFIED SEMINAR TITLE",
  "slug": "verified-seminar-title",
  "date": "2027-01-21",
  "start_time": "12:30",
  "end_time": "13:30",
  "timezone": "America/New_York",
  "event_type": "Research seminar",
  "topic": "Economic analysis and research design",
  "speaker_name": "VERIFIED SPEAKER NAME",
  "speaker_affiliation": "APPROVED AFFILIATION",
  "speaker_slug": "",
  "location": "CONFIRMED LOCATION",
  "abstract": "Speaker-approved abstract.",
  "registration_url": "",
  "materials_url": "",
  "cover_image": "",
  "status": "scheduled",
  "featured": true
}
```

The date and all-uppercase fields above are examples, not real events. **A draft is hidden from the generated site but NOT private in a public GitHub repository.** Store confidential research privately outside the repo.

## Publish a speaker or resource

For speakers: Pages CMS → **Speakers & organizers**. Request approval before posting photographs, bios, job titles, or affiliations. No photo is required; the website uses a simple placeholder. The builder creates individual pages for published speakers.

For resources: Pages CMS → **Research archive entries**. Publish only with author permission and a working HTTPS link. Do not post restricted data, confidential manuscripts, student records, or unapproved proposal documents.

## Student Research & Mentorship and Past Speakers

- **Student Research & Mentorship text:** `content/pages/students.json` or Pages CMS → **Student Research & Mentorship page**.
- **Student Research Spotlight projects:** create JSON entries in `content/student-projects/` or Pages CMS → **Student research projects**. Set `status: draft` until the student has approved public sharing. Only mark published when `consent_confirmed: true` and all project details are ready for public viewing. Do not store sensitive student data in the repository.
- **Past speakers:** Open a speaker profile JSON or Pages CMS → **Speakers & organizers**. Set `past_speaker: true`; then enter `past_talk` and a brief `past_talk_note`. Keep Bandara's `past_speaker` set to false unless he later gives a seminar.

## Contact, research inquiries, and mailing list

Under **Site settings** (`content/site.json`):

- `contact_email`: the destination for the site's inquiry form, initially `sossou.adjisse@wvstateu.edu`.
- `alternate_contact_email`: optional direct-email alternative, initially `sossou.adjisse@gmail.com`.
- `proposal_form_url`: optional published HTTPS Google Forms responder link for a separate submission method.
- `mailing_list_url`: actual mailing-list signup page, if established.

**The inquiry form is a draft generator, not a server-backed submission form.** After visitors fill it out and click **Prepare email inquiry**, their email app opens with a prefilled subject and body. Visitors must send the email themselves. They can also use the direct email links. There is no paid hosting, data collection server, or false success message.

If you later want automatic collection, create a Google Form and paste its public link into `proposal_form_url`. In Google Forms, enable response email notifications under **Responses → More → Get email notifications for new responses**. If you share a public form link, confirm the account's responder settings first.

## Preview, test, publish

```bash
python3 scripts/build.py
python3 scripts/check_site.py
python3 scripts/build.py --serve
```

After reviewing the local site, `git add .`, `git commit`, and `git push origin main`. GitHub Actions handles deployment. Pages CMS edits saved on `main` may publish at once.
