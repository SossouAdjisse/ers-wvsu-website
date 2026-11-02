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

/* Local, serverless research-inquiry form. Intentionally does not claim to send mail. */
(() => {
  const form = document.getElementById('research-inquiry');
  if (!form) return;
  form.addEventListener('submit', event => {
    event.preventDefault();
    if (!form.reportValidity()) return;
    const data = new FormData(form);
    const v = key => String(data.get(key) || '').trim();
    let routes = {};
    try { routes = JSON.parse(form.dataset.recipientMap || '{}'); } catch (_) {}
    const recipient = routes[v('inquiry_type')] || form.dataset.recipient;
    if (!recipient || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(recipient)) return;
    const subject = `ERS–WVSU research inquiry: ${v('inquiry_type')}`;
    const body = [
      'ERS–WVSU Research Inquiry', '',
      `Name: ${v('name')}`, `Email: ${v('email')}`,
      `Affiliation: ${v('affiliation') || 'Not provided'}`,
      `Inquiry type: ${v('inquiry_type')}`,
      `Topic: ${v('topic') || 'Not provided'}`,
      '', 'Research question / request:', v('message'), '',
      'Prepared through the ERS–WVSU website.'
    ].join('\r\n');
    const status = document.getElementById('inquiry-status');
    if (status) status.textContent = 'Your email app should open with the draft. Please review it and press Send there. If nothing opens, use the email address shown below.';
    window.location.href = 'mailto:' + recipient + '?subject=' + encodeURIComponent(subject) + '&body=' + encodeURIComponent(body);
  });
})();
