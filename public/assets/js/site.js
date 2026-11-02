/* ERS–WVSU: accessible navigation and optional content filters. No tracking. */
(() => {
  const toggle = document.querySelector('.menu-toggle');
  const nav = document.querySelector('#primary-nav');
  if (toggle && nav) {
    const closeMenu = () => {
      nav.classList.remove('is-open');
      toggle.setAttribute('aria-expanded', 'false');
      toggle.setAttribute('aria-label', 'Open navigation');
    };
    toggle.addEventListener('click', () => {
      const open = !nav.classList.contains('is-open');
      nav.classList.toggle('is-open', open);
      toggle.setAttribute('aria-expanded', String(open));
      toggle.setAttribute('aria-label', open ? 'Close navigation' : 'Open navigation');
    });
    nav.querySelectorAll('a').forEach(link => link.addEventListener('click', closeMenu));
    document.addEventListener('keydown', event => { if (event.key === 'Escape') closeMenu(); });
    document.addEventListener('click', event => {
      if (!nav.contains(event.target) && !toggle.contains(event.target)) closeMenu();
    });
  }
  const search = document.querySelector('[data-filter-input]');
  const select = document.querySelector('[data-filter-select]');
  const cards = Array.from(document.querySelectorAll('[data-search-item]'));
  const empty = document.querySelector('[data-filter-empty]');
  if (!cards.length) return;
  const refresh = () => {
    const term = (search?.value || '').trim().toLocaleLowerCase();
    const topic = select?.value || 'all';
    let shown = 0;
    cards.forEach(card => {
      const match = (!term || (card.dataset.search || '').toLocaleLowerCase().includes(term)) &&
                    (topic === 'all' || topic === card.dataset.topic);
      card.hidden = !match;
      if (match) shown++;
    });
    if (empty) empty.hidden = shown !== 0;
  };
  if (search) search.addEventListener('input', refresh);
  if (select) select.addEventListener('change', refresh);
})();

/* ERS–WVSU V5: direct Formspree submissions with accessible progress & confirmation. */
(() => {
  const form = document.getElementById('research-inquiry');
  if (!form || form.dataset.formspree !== 'true') return;
  const status = document.getElementById('inquiry-status');
  const button = document.getElementById('inquiry-submit');
  const label = button?.querySelector('span');
  form.addEventListener('submit', async event => {
    event.preventDefault();
    if (!form.reportValidity()) return;
    if (!/^https:\/\/formspree\.io\/f\/[a-zA-Z0-9]+$/.test(form.action)) {
      if (status) status.textContent = 'The submission service is not configured correctly. Please use the ERS contact email below.';
      return;
    }
    if (button) button.disabled = true;
    if (label) label.textContent = 'Submitting your inquiry…';
    if (status) { status.textContent = 'Submitting securely…'; status.dataset.state = 'pending'; }
    try {
      const response = await fetch(form.action, {
        method: 'POST',
        body: new FormData(form),
        headers: { 'Accept': 'application/json' }
      });
      if (response.ok) {
        form.reset();
        if (status) {
          status.textContent = 'Thank you. Your inquiry has been submitted to the ERS–WVSU team.';
          status.dataset.state = 'success';
        }
      } else {
        let message = 'The submission could not be completed. Please try again or email contact@erswvsu.com.';
        try {
          const data = await response.json();
          if (Array.isArray(data.errors) && data.errors.length) {
            const details = data.errors.map(item => item.message).filter(Boolean).join(' ');
            if (details) message = details;
          }
        } catch (_) {}
        if (status) { status.textContent = message; status.dataset.state = 'error'; }
      }
    } catch (_) {
      if (status) { status.textContent = 'Unable to reach the submission service. Please try again or contact contact@erswvsu.com.'; status.dataset.state = 'error'; }
    } finally {
      if (button) button.disabled = false;
      if (label) label.textContent = 'Submit research inquiry';
    }
  });
})();
