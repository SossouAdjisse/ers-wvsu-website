# Connect a Porkbun domain to GitHub Pages (after launch)

**Recommendation:** First publish for free at `https://YOUR_USERNAME.github.io/ers-wvsu/`. Only then purchase/register the desired custom domain in Porkbun. `erswvsu.com` and `www.erswvsu.com` are examples only; availability is not established here.

Before registering, decide whether the domain should be owned by you or by WVSU for long-term institutional continuity. Ask university IT and Communications about official branding and the possibility of `ers.wvstateu.edu`.

## For a new `www.your-domain.com` custom domain

1. Register the desired domain in your existing Porkbun account. Domain registration/renewal is separate from GitHub Pages hosting (which is free on GitHub Free public repos within plan limits). Do **not** buy Porkbun web hosting or WordPress hosting for this design.
2. In GitHub, open the ERS repository → **Settings → Pages → Custom domain**, and enter `www.your-domain.com`; click **Save**. Do this *before* creating the DNS pointer.
3. In Porkbun → Domain Management → DNS, create a **CNAME** record:

   - Type: `CNAME`
   - Host: `www`
   - Answer: `YOUR_USERNAME.github.io` (do **not** append `/ers-wvsu`)

4. In `content/site.json`, set `custom_domain` to `www.your-domain.com` **without `https://` or a trailing slash**. Commit and push. This makes all internal URLs point to the domain root instead of `/ers-wvsu/`.
5. Wait for DNS verification, then under GitHub → Settings → Pages, enable **Enforce HTTPS** when available.
6. Optionally set up the apex/root domain (`your-domain.com`) to redirect to `www`. Follow the exact current GitHub instructions for the four `A` records (and optional `AAAA` records), or another GitHub-supported `ALIAS`/`ANAME`. Do not guess DNS records.

**Safety:** Verify your custom domain with GitHub where possible and avoid wildcard DNS records. Domain changes may take up to 24 hours to propagate. Only point Porkbun DNS at GitHub *after* the domain is added in the GitHub Pages repository settings.

Official instructions:
- https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/managing-a-custom-domain-for-your-github-pages-site
- https://porkbun.com/support
