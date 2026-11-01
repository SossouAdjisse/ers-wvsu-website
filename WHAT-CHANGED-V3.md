# ERS–WVSU Website v3 — New pages and communication

This edition builds upon the strategic, economics-centered v2 site. No hosting subscription is needed; it remains compatible with GitHub Pages, local Git editing, and Pages CMS.

## Pages and new features

- **Past Speakers** (`/past-speakers/`) — lists Sossou S. Adjisse and Frehot Hailou as previous presenters, with carefully worded presentation topics. Bandara is not marked as a previous presenter. Add or revise dates and presentation titles only after checking the seminar records.
- **People** (`/speakers/`) — includes Sossou S. Adjisse, Frehot Hailou, and Saman Bandara, each with an editable biography and a dedicated profile page. People can have different statuses (organizer, prior presenter, featured faculty); a profile does *not* automatically denote a formal ERS leadership position.
- **Student Research & Mentorship** (`/students/`) — includes an approved-work **Student Research Spotlight** plus potential mentorship pathways. The initial spotlight does not invent named student projects.
- **Get involved** — now includes a styled inquiry form collecting name, email, affiliation, inquiry purpose, optional subject, and a short project description. The default form **opens a draft in the visitor's email client** addressed to `sossou.adjisse@wvstateu.edu`. Visitors must click **Send** there; the site does not send or store messages itself. A direct Gmail alternative appears below.

## Email and optional automatic form submissions

To change the email destination, edit `content/site.json` → `contact_email` or Pages CMS → **Site settings → Primary contact email**. For the Gmail alternative, change `alternate_contact_email`.

For a form that records submissions **without requiring visitors to open an email app**, create a Google Form under your own Google account, allow access to intended respondents, publish it, then add its public responder link to `proposal_form_url` in `content/site.json`. The Get Involved page will show a **Google proposal form** button. For notification emails, use Google Forms → Responses → three-dot menu → **Get email notifications for new responses** (subject to your account's controls). Google Forms can also be embedded in the page later if desired.

**Important:** Google's automatic form notifications are configured by the form owner inside Google Forms, not by setting an arbitrary recipient address in this ZIP. If using a WVSU managed account, verify external responder settings and approval requirements with university IT.

## Student research privacy

Entries in `content/student-projects/` must specify `status: "published"` and `consent_confirmed: true` before the builder makes them public. A published student record must also include a name and project title. Obtain appropriate permission before including a student's name, project, photograph, or research materials. Do not place protected student information or sensitive drafts in the public GitHub repository—even draft files are public in the repository.

## Confirmations before launch

- Confirm Hailou and Bandara's agreement with their public ERS–WVSU profile text (and photographs, if added).
- Verify exact seminar dates and titles before adding them as historical event records.
- Confirm the institutional branding and the role of the initiative.
- Test that the email form opens the correct email app **and** that an actual test message reaches the correct inbox.
- The domain remains unconfigured until GitHub Pages and Porkbun setup are completed.
