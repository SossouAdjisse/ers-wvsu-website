#!/usr/bin/env python3
"""ERS–WVSU zero-dependency static website builder.

Run `python3 scripts/build.py` then `python3 -m http.server 8000 -d dist`.
For GitHub Pages the base URL is automatically derived from GITHUB_REPOSITORY.
Set a verified custom_domain in content/site.json to use / paths instead.
"""
from __future__ import annotations
import argparse
import datetime as dt
import html
import json
import os
import re
import shutil
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'dist'
CONTENT = ROOT / 'content'
SITE = {}
BASE = '/'
THEMES = []
CAPABILITIES = []
PATHWAY = []
APPEARANCE = {}
EVENTS = []
SPEAKERS = []
RESOURCES = []
STUDENT_PROJECTS = []
AFFILIATES = []
COMMUNITY_ROLES = []
PAGES = {}
NAV = [('index.html', 'Home', 'home'), ('partnerships/', 'Partnerships', 'partnerships'), ('seminars/', 'Seminars', 'seminars'), ('past-speakers/', 'Past speakers', 'past'), ('speakers/', 'People', 'speakers'), ('students/', 'Students', 'students'), ('get-involved/', 'Get involved', 'involved'), ('about/', 'About', 'about')]
ICONS = {
    'arrow': '<path d="M4 12h16m-7-7 7 7-7 7"/>',
    'up-right': '<path d="M6 18 18 6M7 6h11v11"/>',
    'calendar': '<rect x="3" y="5" width="18" height="16" rx="2"/><path d="M16 3v4M8 3v4M3 10h18"/>',
    'clock': '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l4 2"/>',
    'pin': '<path d="M20 10c0 5-8 12-8 12S4 15 4 10a8 8 0 1 1 16 0Z"/><circle cx="12" cy="10" r="2.5"/>',
    'speaker': '<path d="M12 17a5 5 0 0 0 5-5V7a5 5 0 0 0-10 0v5a5 5 0 0 0 5 5ZM5 12a7 7 0 0 0 14 0M12 19v3m-4 0h8"/>',
    'book': '<path d="M12 7c-3-2-6-2-9-1v14c3-1 6-1 9 1 3-2 6-2 9-1V6c-3-1-6-1-9 1Zm0 0v14"/>',
    'landscape': '<path d="m2 19 6-8 4 4 4-7 6 11H2Z"/><circle cx="7" cy="6" r="2"/>',
    'leaf': '<path d="M21 3C10 3 4 8 4 16a5 5 0 0 0 5 5c8 0 12-6 12-18ZM4 20c4-7 7-9 12-12"/>',
    'building': '<path d="M4 21V9l8-5 8 5v12M2 21h20M9 21v-7h6v7M8 10h.01M16 10h.01"/>',
    'briefcase': '<rect x="3" y="7" width="18" height="14" rx="2"/><path d="M8 7V5a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2M3 13c6 4 12 4 18 0"/>',
    'chart': '<path d="M4 20V4M4 20h17M8 16l4-5 4 3 5-7"/>',
    'users': '<circle cx="9" cy="8" r="3"/><path d="M3 21v-3a6 6 0 0 1 12 0v3M17 5a3 3 0 0 1 0 6M17 15a5 5 0 0 1 4 5v1"/>',
    'search': '<circle cx="10" cy="10" r="7"/><path d="m15 15 6 6"/>',
    'check': '<path d="m4 12 5 5L20 6"/>',
    'download': '<path d="M12 3v13m-5-5 5 5 5-5M4 17v4h16v-4"/>',
    'mail': '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 7 9 6 9-6"/>',
    'plus': '<path d="M12 5v14M5 12h14"/>',
    'file': '<path d="M6 3h9l4 4v14H6V3Zm9 0v5h5M9 13h7M9 17h7"/>',
    'spark': '<path d="M12 2v20M2 12h20M5 5l14 14M19 5 5 19"/>',
    'compass': '<circle cx="12" cy="12" r="9"/><path d="m15 9-2 5-5 2 2-5 5-2Z"/>',
    'target': '<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="5"/><circle cx="12" cy="12" r="1"/>',
    'scales': '<path d="M12 3v18M5 6h14M4 20h16M4 10l-2 5h8l-2-5M16 10l-2 5h8l-2-5"/>',
}


def e(v): return html.escape(str(v if v is not None else ''), quote=True)


def jload(path): return json.loads((ROOT / path).read_text(encoding='utf-8'))


def collection(kind):
    arr = []
    for path in sorted((CONTENT / kind).glob('*.json')):
        record = json.loads(path.read_text(encoding='utf-8'))
        if not isinstance(record, dict):
            raise ValueError(f'{path}: expected JSON object')
        record['_source'] = str(path.relative_to(ROOT))
        arr.append(record)
    return arr


def internal(path=''):
    return BASE + str(path).lstrip('/')


def public_url(raw):
    """Turn site-local CMS asset paths into project-safe paths; filter unsafe URLs."""
    raw = (raw or '').strip()
    if not raw: return ''
    if raw.startswith('http://') or raw.startswith('https://'):
        return raw
    if raw.startswith('mailto:'):
        return raw
    if raw.startswith('//') or ':' in raw.split('/')[0]:
        return ''
    return internal(raw)


def remote_url(raw):
    raw = (raw or '').strip()
    parsed = urlparse(raw)
    return raw if parsed.scheme in ('http', 'https') and parsed.netloc else ''


def valid_mail(addr):
    return bool(re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+', (addr or '').strip()))


def icon(key, size=20, cls=''):
    contents = ICONS.get(key, ICONS['spark'])
    return f'<svg aria-hidden="true" class="icon {e(cls)}" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.65" stroke-linecap="round" stroke-linejoin="round">{contents}</svg>'


def eyebrow(content, on_dark=False):
    return f'<p class="eyebrow {"eyebrow--light" if on_dark else ""}"><span class="eyebrow-dot" aria-hidden="true"></span>{e(content)}</p>'


def button(label, dest, kind='gold', ico='up-right', extra=''):
    return f'<a class="btn btn--{kind} {e(extra)}" href="{e(dest)}"><span>{e(label)}</span>{icon(ico,18)}</a>'


def intro_header(label, heading, emphasis, intro, variant='dark'):
    return f'''<section class="page-hero page-hero--{e(variant)}"><div class="container page-hero__inner">
       {eyebrow(label, variant=='dark')}<h1>{e(heading)} <em>{e(emphasis)}</em></h1>
       <p class="page-hero__intro">{e(intro)}</p><div class="page-hero__rule" aria-hidden="true"></div>
    </div></section>'''


def head_html(title, description, current):
    favicon = internal('assets/images/favicon.svg')
    css = internal('assets/css/site.css')
    appearance_css = internal('assets/css/appearance.css')
    js = internal('assets/js/site.js')
    domain = str(SITE.get('custom_domain','')).strip()
    canonical = ''
    if domain:
        domain = domain.replace('https://','').replace('http://','').strip('/ ')
        canonical = f'<link rel="canonical" href="https://{e(domain)}{internal(current)}">'
    return f'''<!doctype html>
<html lang="en"><head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="light"><meta name="theme-color" content="#151915">
<title>{e(title)} | ERS–WVSU</title><meta name="description" content="{e(description)}">
<meta property="og:type" content="website"><meta property="og:title" content="{e(title)} — ERS–WVSU"><meta property="og:description" content="{e(description)}">
<link rel="icon" href="{e(favicon)}" type="image/svg+xml">{canonical}
<link rel="stylesheet" href="{e(css)}"><link rel="stylesheet" href="{e(appearance_css)}"><script src="{e(js)}" defer></script>
</head><body><a class="skip-link" href="#main">Skip to main content</a>'''


def nav_html(active):
    links = []
    for path, label, key in NAV:
        is_active = key == active
        active_class = 'is-active' if is_active else ''
        current_page = ' aria-current="page"' if is_active else ''
        links.append(f'<a href="{e(internal(path))}" class="nav-link {active_class}"{current_page}>{e(label)}</a>')
    return f'''<div class="site-announcement"><div class="container announcement-inner"><span><span class="status-spark" aria-hidden="true"></span> ECONOMICS-CENTERED RESEARCH EXCHANGE</span><span class="announcement-right">WEST VIRGINIA STATE UNIVERSITY <span class="bullet">·</span> EST. 2026</span></div></div>
<header class="site-header" id="site-header">
  <div class="container header-brand-row"><a class="brand" href="{e(internal('index.html'))}" aria-label="ERS–WVSU home"><span class="brand-mark">E<span class="brand-period">.</span>R.S<span class="brand-period">.</span></span><span class="brand-rule" aria-hidden="true"></span><span class="brand-name">Economic Research Seminar<span>West Virginia State University</span></span></a>
    <p class="header-purpose">ECONOMIC REASONING <span>·</span> DATA ANALYSIS <span>·</span> CAUSAL INFERENCE</p>
    <button class="menu-toggle" type="button" aria-controls="primary-nav" aria-expanded="false" aria-label="Open navigation"><span></span><span></span><span></span></button>
  </div>
  <div class="site-nav-row"><div class="container site-nav-inner"><nav class="primary-nav" id="primary-nav" aria-label="Main navigation">{''.join(links)}</nav></div></div>
</header>'''

def channel_address(channel):
    """Public ERS email addresses; forwarding itself remains configured in Porkbun."""
    key='contact_email' if channel=='contact' else 'email_'+channel
    value=str(SITE.get(key,'')).strip()
    return value if valid_mail(value) else ''


def channel_link(channel, text=None, css_class='inline-link'):
    address=channel_address(channel)
    if not address: return ''
    return f'<a class="{e(css_class)}" href="mailto:{e(address)}">{e(text or address)}</a>'


def contact_strip(title, introduction, channels):
    cards=[]
    for channel,label in channels:
        address=channel_address(channel)
        if not address: continue
        cards.append(f'<a class="contact-route-card" href="mailto:{e(address)}">'
                     f'<span class="contact-route-label">{e(label)}</span>'
                     f'<strong>{e(address)}</strong>{icon("up-right",16)}</a>')
    if not cards: return ''
    return (f'<section class="section contact-route-section"><div class="container contact-route-wrap">'
            f'<div class="contact-route-header">{eyebrow("CONTACT THE RELEVANT TEAM")}'
            f'<h2>{e(title)}</h2><p>{e(introduction)}</p></div>'
            f'<div class="contact-route-grid">{"".join(cards)}</div></div></section>')


def email_directory():
    entries=[
        ('contact','General inquiries','General questions about ERS–WVSU.'),
        ('seminars','Seminars & events','Seminar proposals, schedules, and presentations.'),
        ('speakers','Speaker relations','Speaker invitations, biographies, and past talks.'),
        ('partnerships','Research partnerships','Collaborative projects across disciplines and institutions.'),
        ('research','Research & methods','Economics, quantitative analysis, and causal inference.'),
        ('grants','Grants & funding','Collaborative research proposals and funding discussions.'),
        ('students','Student research','Student project submissions and research spotlight.'),
        ('mentorship','Research mentorship','Mentoring and skill-building opportunities.'),
        ('outreach','Outreach','Community and external engagement.'),
    ]
    cards=[]
    for channel,label,desc in entries:
        address=channel_address(channel)
        if not address: continue
        cards.append(f'<article class="email-directory-card"><span class="mini-label">{e(label)}</span>'
                     f'<a href="mailto:{e(address)}">{e(address)} {icon("up-right",16)}</a>'
                     f'<p>{e(desc)}</p></article>')
    return (f'<section class="section email-directory-section" id="email-directory">'
            f'<div class="container">{section_label("03","DIRECT CONTACT DIRECTORY")}'
            f'<div class="section-heading-row"><h2>Find the right<br><em>point of contact.</em></h2>'
            f'<p>Choose the address that best fits your inquiry. Each address is managed by the ERS–WVSU team; '
            f'please send confidential research details only after agreeing on an appropriate channel.</p></div>'
            f'<div class="email-directory-grid">{"".join(cards)}</div></div></section>')


def footer_html():
    nav = ''.join(f'<a href="{e(internal(path))}">{e(label)}</a>' for path,label,key in NAV if key!='home') + f'<a href="{e(internal("archive/"))}">Research resources</a>'
    uni = remote_url(SITE.get('university_url',''))
    right = f'<a href="{e(uni)}" target="_blank" rel="noopener noreferrer">West Virginia State University {icon("up-right", 14)}</a>' if uni else ''
    mail = SITE.get('contact_email','').strip()
    contact = f'<a href="mailto:{e(mail)}">{e(mail)}</a>' if valid_mail(mail) else '<span>Contact details forthcoming</span>'
    seminars=channel_link('seminars')
    partners=channel_link('partnerships')
    year = dt.date.today().year
    return f'''<footer class="footer"><div class="container"><div class="footer-grid">
<div class="footer-intro">{eyebrow('STRONGER EVIDENCE THROUGH COLLABORATION',True)}<h2>More rigorous questions.<br><em>More useful evidence.</em></h2><p>{e(SITE.get('footer_note',''))}</p></div>
<div class="footer-linkcol"><h3>EXPLORE</h3>{nav}</div>
<div class="footer-linkcol"><h3>CONNECT</h3><a href="{e(internal('get-involved/'))}">Present your research {icon('up-right',14)}</a>{contact}{seminars}{partners}{right}</div>
</div><div class="footer-bottom"><span>© {year} ERS–WVSU. Website content maintained by the seminar organizers.</span><span>Faculty-led research initiative · Branding pending institutional review.</span></div></div></footer>'''


def shell(active, title, description, content, route):
    return head_html(title, description, route) + nav_html(active) + f'<main id="main">{content}</main>' + footer_html() + '</body></html>'


def section_label(num, text):
    return f'<p class="section-label"><span>{e(num)}</span> / {e(text)}</p>'


def pretty_date(s):
    try:
        return dt.date.fromisoformat(s).strftime('%B %-d, %Y')
    except (ValueError,TypeError):
        try: return dt.date.fromisoformat(s).strftime('%B %d, %Y')
        except: return 'Date to be announced'


def dayparts(s):
    try:
        d=dt.date.fromisoformat(s)
        return (d.strftime('%b').upper(),d.strftime('%d'))
    except: return ('TBA','—')


def is_published(ev): return ev.get('status') in ('scheduled','completed')


def future_ev(ev):
    if ev.get('status') != 'scheduled': return False
    try: return dt.date.fromisoformat(ev['date']) >= dt.date.today()
    except: return False


def schedule():
    return sorted((x for x in EVENTS if is_published(x) and future_ev(x)),key=lambda x:x.get('date',''))


def completed():
    return sorted((x for x in EVENTS if x.get('status')=='completed'), key=lambda x:x.get('date',''),reverse=True)


def upcoming_unknown():
    return [x for x in EVENTS if x.get('status')=='scheduled' and not future_ev(x)]


def speaker_image(s, cls='avatar'):
    src=public_url(s.get('photo',''))
    if src:
        return f'<img class="{e(cls)}" src="{e(src)}" alt="Portrait of {e(s.get("name","speaker"))}" loading="lazy">'
    initials=''.join([w[0] for w in re.sub(r'(?i)\b(phd|ph|d|dr)\b','',s.get('name','')).replace('.','').split()[:2]]).upper() or 'ERS'
    return f'<div class="{e(cls)} avatar--placeholder" aria-label="No photograph available"><span>{e(initials)}</span><span class="avatar-ring" aria-hidden="true"></span></div>'


def event_card(ev, compact=False):
    mon,day=dayparts(ev.get('date'))
    title=ev.get('title','Untitled session')
    url=internal('seminars/'+ev['slug']+'/')
    is_comp=ev.get('status')=='completed'
    return f'''<article class="event-card {"event-card--compact" if compact else ""}" data-search-item data-search="{e(title+' '+ev.get('speaker_name','')+' '+ev.get('topic',''))}" data-topic="{e(ev.get('topic',''))}">
<div class="event-date" aria-label="{e(pretty_date(ev.get('date','')))}"><span>{e(mon)}</span><strong>{e(day)}</strong></div>
<div class="event-main"><div class="event-kicker"><span>{e(ev.get('event_type','Seminar'))}</span><span class="kicker-divider"></span><span>{e(ev.get('topic','Research'))}</span></div><h3><a href="{e(url)}">{e(title)}</a></h3>
<p class="event-presenter">{e(ev.get('speaker_name','Speaker to be announced'))} {('· '+e(ev['speaker_affiliation'])) if ev.get('speaker_affiliation') else ''}</p>
<div class="event-meta">{icon('calendar',15)} {e(pretty_date(ev.get('date','')))} {(' · '+e(ev.get('time_label') or ev.get('start_time',''))) if ev.get('start_time') else ''} <span class="event-meta-sep">·</span> {e(ev.get('location','Location forthcoming'))}</div></div>
<div class="event-go"><a href="{e(url)}" aria-label="Details for {e(title)}">{icon('up-right',22)}</a></div></article>'''


def pathway_cards():
    return ''.join(f'''<article class="pathway-card"><span class="pathway-step">{i:02d}</span><h3>{e(item.get('title',''))}</h3><p>{e(item.get('description',''))}</p></article>''' for i,item in enumerate(PATHWAY,1))


def render_home():
    c = PAGES['home']
    upcoming = schedule()
    if upcoming:
        ev = upcoming[0]
        next_box = f'''<div class="next-panel"><div class="next-panel__top"><span class="live-dot"></span> NEXT SEMINAR <span class="next-panel__date">{e(pretty_date(ev.get('date','')))}</span></div><h3>{e(ev.get('title',''))}</h3><p>{e(ev.get('speaker_name',''))}</p><a class="inline-link" href="{e(internal('seminars/'+ev['slug']+'/'))}">View seminar details {icon('up-right',16)}</a></div>'''
    else:
        next_box = f'''<div class="next-panel"><div class="next-panel__top"><span class="live-dot"></span> SEMINAR PROGRAM <span class="next-panel__date">IN DEVELOPMENT</span></div><h3>Research in progress.<br>Evidence in conversation.</h3><p>Confirmed talks will be posted here with their speakers, dates, and locations. Projects seeking an economic contribution are welcome to inquire.</p><div class="next-panel__foot"><span>{icon('check',16)} Economics-led dialogue</span><span>{icon('calendar',16)} Schedule forthcoming</span></div></div>'''
    cards=[]
    for i in range(1,4):
        cards.append(f'''<article class="purpose-card"><div class="purpose-card__top"><span>0{i}</span>{icon('up-right',21)}</div><h3>{e(c.get(['','pillar_one_title','pillar_two_title','pillar_three_title'][i],''))}</h3><p>{e(c.get(['','pillar_one_text','pillar_two_text','pillar_three_text'][i],''))}</p></article>''')
    topic_cards=[]
    for item in THEMES:
        topic_cards.append(f'''<article class="topic-card">{icon(item.get('icon','chart'),27)}<h3>{e(item.get('title',''))}</h3><p>{e(item.get('description',''))}</p></article>''')
    return f'''
<section class="home-hero"><div class="container home-hero__grid"><div class="home-hero__copy">
{eyebrow(c.get('eyebrow',''),True)}
<h1>{e(c.get('headline_line_one',''))}<br><em>{e(c.get('headline_line_two',''))}</em></h1>
<p class="home-hero__intro">{e(c.get('intro',''))}</p>
<div class="hero-actions">{button('See how we collaborate',internal('partnerships/'))}{button('Propose a research conversation',internal('get-involved/#propose'),'outline')}</div>
<div class="hero-caption"><span></span> ECONOMIC FRAMING · DATA ANALYSIS · CAUSAL INFERENCE</div>
</div><div class="hero-art"><img src="{e(internal('assets/images/hero-network.svg'))}" alt="Conceptual network of research ideas linked by gold connections" width="900" height="800" fetchpriority="high"><div class="hero-art__header"><span>ECONOMICS × RESEARCH / EXCHANGE</span>{icon('spark',18)}</div><a class="hero-art__bottom" href="{e(internal('partnerships/'))}"><span class="hero-art__symbol">{icon('spark',25)}</span><span><small>THE ERS–WVSU APPROACH</small><strong>Better questions · Credible methods · Shared research</strong></span>{icon('up-right',21)}</a></div></div></section>
<div class="audience-strip"><div class="container audience-strip__inner"><span class="audience-label">WORKING ACROSS</span><span>Agriculture</span><span class="strip-plus">·</span><span>Education</span><span class="strip-plus">·</span><span>Health</span><span class="strip-plus">·</span><span>Business</span><span class="strip-plus">·</span><span>Natural sciences & policy</span></div></div>
<section class="section purpose-section"><div class="container">
{section_label('01','THE VALUE WE ADD')}<div class="section-intro"><h2>{e(c.get('section_one_title',''))}<br><em>{e(c.get('section_one_emphasis',''))}</em></h2><p>{e(c.get('section_one_intro',''))}</p></div>
<div class="purpose-grid">{''.join(cards)}</div><div class="section-outro"><p>Bring disciplinary expertise; explore what economics and credible empirical research can add.</p><a class="inline-link" href="{e(internal('partnerships/'))}">Explore research partnerships {icon('up-right',19)}</a></div></div></section>
<section class="section section--sand pathway-section"><div class="container">{section_label('02','OUR COLLABORATION MODEL')}<div class="section-heading-row"><h2>From a research idea<br><em>to a testable contribution.</em></h2><p>Each collaboration begins with a real disciplinary question. We explore the economic and empirical angle, then agree on next steps and contributions.</p></div><div class="pathway-grid">{pathway_cards()}</div><a href="{e(internal('partnerships/'))}" class="inline-link pathway-more">See our research approach {icon('up-right',19)}</a></div></section>
<section class="section next-section"><div class="container next-grid"><div class="research-visual"><img src="{e(internal('assets/images/research-rings.svg'))}" width="960" height="600" loading="lazy" alt="Abstract research network representing reciprocal exchange and evidence"><div class="research-visual__note">THE QUESTION <span>→</span> THE DESIGN <span>→</span> THE EVIDENCE</div></div>
<div class="next-section__copy">{section_label('03','THE SEMINAR SERIES')}<h2>Focused discussion.<br><em>Real research value.</em></h2>{next_box}<a class="inline-link" href="{e(internal('seminars/'))}">Explore seminars and events {icon('up-right',19)}</a></div></div></section>
<section class="section topics-section"><div class="container">{section_label('04','ILLUSTRATIVE RESEARCH THEMES')}<div class="section-heading-row"><div><h2>Economic questions<br><em>in every field.</em></h2></div><p>These themes demonstrate the breadth of possible collaboration. They are not announcements of projects, grants, or institutional partnerships.</p></div><div class="topics-grid">{''.join(topic_cards)}</div><p class="themes-note">Representative areas of interest only. Detailed proposals and unannounced research remain with their respective teams.</p></div></section>
<section class="section region-section"><div class="container region-grid"><div>{section_label('05','A PRECISE INTERDISCIPLINARY MISSION')}<h2>{e(c.get('regional_title',''))}<br><em>{e(c.get('regional_emphasis',''))}</em></h2></div><div class="region-content"><p>{e(c.get('regional_text',''))}</p>{button('Our selection principles',internal('partnerships/#research-fit'))}</div></div></section>
<section class="section participation-section"><div class="container participation-grid"><div>{section_label('06','START A RESEARCH CONVERSATION')}<h2>{e(c.get('closing_title',''))}<br><em>{e(c.get('closing_emphasis',''))}</em></h2><p>{e(c.get('closing_text',''))}</p></div>
<div class="action-links"><a href="{e(internal('get-involved/#propose'))}">Propose a seminar or collaboration {icon('up-right',22)}</a><a href="{e(internal('partnerships/'))}">See what economics can add {icon('up-right',22)}</a><a href="{e(internal('students/'))}">Student research & mentorship {icon('up-right',22)}</a></div></div></section>'''+render_newsletter_feature()


def render_partnerships():
    c=PAGES['partnerships']
    cards=''.join(f'''<article class="capability-card"><div class="capability-icon">{icon(item.get('icon','chart'),27)}</div><h3>{e(item.get('title',''))}</h3><p>{e(item.get('description',''))}</p></article>''' for item in CAPABILITIES)
    checks=''.join(f'''<article class="fit-item"><span>{icon('check',19)}</span><div><h3>{e(c.get('fit_'+k+'_title',''))}</h3><p>{e(c.get('fit_'+k+'_text',''))}</p></div></article>''' for k in ('one','two','three'))
    campus_link=remote_url(c.get('campus_news_url',''))
    source=f'<a href="{e(campus_link)}" target="_blank" rel="noopener noreferrer" class="inline-link">Read WVSU’s announcement {icon("up-right",17)}</a>' if campus_link else ''
    return f'''{intro_header(c['eyebrow'],c['heading'],c['heading_emphasis'],c['intro'])}
<section class="section capabilities-section"><div class="container">{section_label('01','RESEARCH DEVELOPMENT CAPABILITIES')}<div class="section-heading-row"><h2>{e(c['services_heading'])}</h2><p>{e(c['services_intro'])}</p></div><div class="capability-grid">{cards}</div></div></section>
<section class="section section--sand" id="collaboration-path"><div class="container">{section_label('02','HOW COLLABORATION WORKS')}<div class="section-heading-row"><h2>{e(c['pathway_heading'])}</h2><p>{e(c['pathway_intro'])}</p></div><div class="pathway-grid">{pathway_cards()}</div></div></section>
<section class="section fit-section" id="research-fit"><div class="container fit-grid"><div>{section_label('03','WHO SHOULD PRESENT')}<h2>{e(c['fit_heading'])}</h2><p class="lead-paragraph">{e(c['fit_intro'])}</p><div class="fit-tip">A project <strong>does not need a finished economics component</strong> to qualify. It does need a plausible opportunity for one.</div></div><div class="fit-list">{checks}</div></div></section>
<section class="section campus-section"><div class="container campus-grid"><div>{section_label('04','RESEARCH CONTEXT AT WVSU')}<h2>{e(c['campus_title'])}</h2></div><div><p class="lead-paragraph">{e(c['campus_text'])}</p>{source}</div></div></section>
<section class="section partner-cta"><div class="container partner-cta-grid"><div>{section_label('05','WORK WITH ERS–WVSU')}<h2>Have a question<br><em>that could become stronger?</em></h2><p>We welcome initial conversations about the economic or empirical contribution to your work.</p></div>{button('Propose a collaboration',internal('get-involved/#propose'))}</div></section>'''+contact_strip(
    'Collaborate with ERS–WVSU', 'Connect directly about partnership development, empirical research, or proposals.',
    [('partnerships','Research partnerships'),('research','Economic analysis & methods'),('grants','Research grants')])


def render_seminars():
    c = PAGES['seminars']
    upcoming = schedule()
    past = completed()
    now = dt.date.today()
    if upcoming:
        upcoming_html=''.join(event_card(x) for x in upcoming)
    else:
        upcoming_html=f'''<div class="empty-state empty-state--large"><div class="empty-state__icon">{icon('calendar',29)}</div><div><p class="mini-label">SCHEDULE IN DEVELOPMENT</p><h3>{e(c.get('next_empty_title',''))}</h3><p>{e(c.get('next_empty_text',''))}</p><a class="inline-link" href="{e(internal('get-involved/#propose'))}">Express interest in presenting {icon('up-right',16)}</a></div></div>'''
    if past:
        past_html=''.join(event_card(x,True) for x in past)
    else:
        past_html=f'''<div class="archive-empty"><span class="archive-empty__rule"></span><div><h3>Our seminar history starts here.</h3><p>Completed sessions and approved materials will be added when their details are verified.</p></div>{icon('arrow',27)}</div>'''
    return f'''{intro_header(c['eyebrow'],c['heading'],c['heading_emphasis'],c['intro'])}
<section class="section events-main"><div class="container">
<div class="section-heading-row section-heading-row--event">{section_label('01','UPCOMING SESSIONS')}<span class="muted-note">All times Eastern · Institute, West Virginia</span></div><div class="events-list">{upcoming_html}</div>
<div class="past-header">{section_label('02','PAST SESSIONS')}<h2>Conversations worth<br><em>revisiting.</em></h2></div><div class="events-list">{past_html}</div><div class="extra-link-row">{button('Meet past speakers',internal('past-speakers/'),'outline-dark')}</div></div></section>
<section class="section section--sand"><div class="container format-grid"><div class="format-art">{icon('target',76)}<span>ECONOMICS · DATA · CAUSAL IDENTIFICATION</span></div><div>{section_label('03','THE SEMINAR FORMAT')}<h2>{e(c['format_title'])}</h2><p class="lead-paragraph">{e(c['format_text'])}</p>{button('Presentation criteria',internal('partnerships/#research-fit'))}</div></div></section>'''+contact_strip(
    'Interested in presenting?', 'Contact the seminar team for schedules, submissions, and speaker coordination.',
    [('seminars','Seminar proposals'),('speakers','Speaker invitations')])


def speaker_card(sp):
    href = internal('speakers/'+sp['slug']+'/')
    return f'''<article class="speaker-card" data-search-item data-search="{e(sp.get('name','')+' '+sp.get('expertise','')+' '+sp.get('affiliation',''))}">
<a href="{e(href)}" class="speaker-card__image" aria-label="Read profile of {e(sp.get('name'))}">{speaker_image(sp,'speaker-card__avatar')}<span class="speaker-card__corner">{icon('up-right',20)}</span></a>
<div class="speaker-card__text"><span class="mini-label">{e(sp.get('role','SPEAKER'))}</span><h3><a href="{e(href)}">{e(sp.get('name',''))}</a></h3><p>{e(sp.get('position',''))}</p><span>{e(sp.get('affiliation',''))}</span></div></article>'''


def render_speakers():
    """One ERS community: faculty first, followed by student participants."""
    c = PAGES['speakers']
    participants = [p for p in AFFILIATES if p.get('status') == 'published']
    participants.sort(key=lambda p: (p.get('sort_order', 999), p.get('name', '')))
    def is_student(person):
        return (person.get('participant_type') == 'student' or
                str(person.get('participation', '')).startswith('Student Participant'))
    faculty = [p for p in participants if not is_student(p)]
    students = [p for p in participants if is_student(p)]
    published_profiles = {s.get('slug') for s in SPEAKERS if s.get('status') == 'published'}

    def member_card(person):
        name = e(person.get('name', ''))
        position = e(person.get('position', ''))
        affiliation = e(person.get('affiliation', 'West Virginia State University'))
        kind = 'student' if is_student(person) else 'faculty'
        default_role = 'Student Participant & Supporter' if kind == 'student' else 'Faculty Participant & Supporter'
        participation = e(person.get('participation') or default_role)
        portrait_record = dict(person)
        if not portrait_record.get('photo'):
            detail = next((s for s in SPEAKERS if s.get('slug') == person.get('slug')), {})
            if detail.get('photo'):
                portrait_record['photo'] = detail['photo']
        portrait = speaker_image(portrait_record, 'community-member__portrait')
        profile_link = ''
        if kind == 'faculty' and person.get('slug') in published_profiles:
            profile_link = (f'<a class="community-member__profile-link" '
                f'href="{e(internal("speakers/"+person["slug"]+"/"))}">'
                f'View Profile {icon("up-right",14)}</a>')
        return (
            f'<article class="community-member" data-member-kind="{kind}" '
            f'data-member-slug="{e(person.get("slug", ""))}">'
            f'<div class="community-member__image">{portrait}</div>'
            f'<div class="community-member__details">'
            f'<h3>{name}</h3>'
            f'<p class="community-member__title">{position}</p>'
            f'<p class="community-member__institution">{affiliation}</p>'
            f'{profile_link}</div>'
            f'<div class="community-member__role">{participation}</div>'
            f'</article>'
        )

    faculty_cards = ''.join(member_card(person) for person in faculty)
    student_section = ''
    if students:
        student_cards = ''.join(member_card(person) for person in students)
        student_section = (
            '<div class="student-community-block" id="student-community">'
            '<div class="section-heading-row"><h2>Student participants<br>'
            '<em>and supporters.</em></h2>'
            '<p>Students are part of the ERS–WVSU research and seminar community. '
            'We welcome their participation, questions, and perspectives.</p></div>'
            f'<div class="community-roster-grid community-roster-grid--students">{student_cards}</div>'
            '</div>'
        )
    role_html = ''.join(
        f'<article class="community-role"><span class="role-index">{i:02d}</span>'
        f'<h3>{e(item.get("title", ""))}</h3>'
        f'<p>{e(item.get("description", ""))}</p></article>'
        for i, item in enumerate(COMMUNITY_ROLES, 1)
    )
    return f'''{intro_header(c['eyebrow'], c['heading'], c['heading_emphasis'], c['intro'])}
<section class="section community-roster-section" id="research-community"><div class="container">
{section_label('01', 'ERS–WVSU RESEARCH & SEMINAR COMMUNITY')}
<div class="section-heading-row"><h2>One community.<br><em>Many contributions.</em></h2>
<p>ERS–WVSU brings together faculty and students from economics, business, management,
and other disciplines. Coordination and participation roles recognize the shared work
behind our research exchange.</p></div>
<div class="community-roster-grid community-roster-grid--faculty">{faculty_cards}</div>
{student_section}
</div></section>
<section class="section community-contributions" id="ways-to-contribute"><div class="container">
{section_label('02', 'WAYS TO PARTICIPATE')}
<div class="section-heading-row"><h2>Make room for<br><em>every contribution.</em></h2>
<p>Faculty, students, and external collaborators can explore the roles below as
ERS–WVSU grows. Participation is voluntary, with responsibilities agreed together.</p></div>
<div class="community-role-grid">{role_html}</div>
</div></section>
<section class="section section--sand"><div class="container invitation-band"><div>
{section_label('03', 'JOIN THE RESEARCH COMMUNITY')}
<h2>{e(c['invitation_title'])}</h2><p>{e(c['invitation_text'])}</p></div>
{button('Explore a role or collaboration', internal('get-involved/#propose'))}
</div></section>'''


def render_past_speakers():
    c=PAGES['past-speakers']
    past=sorted([sp for sp in SPEAKERS if sp.get('status')=='published' and sp.get('past_speaker')],key=lambda sp:(sp.get('past_talk_date',''),sp.get('name','')),reverse=True)
    cards=[]
    for sp in past:
        dat=pretty_date(sp.get('past_talk_date','')) if sp.get('past_talk_date') else 'Date not yet recorded'
        time=sp.get('past_talk_time','')
        detail=sp.get('past_talk_summary','') or sp.get('past_talk_note','')
        eventslug={'sossou-s-adjisse':'economics-as-a-meeting-place-2026','frehot-hailou':'alcohol-policy-and-school-attendance-2026'}.get(sp.get('slug'))
        eventlink=(f'<a class="inline-link" href="{e(internal("seminars/"+eventslug+"/"))}">Read seminar summary {icon("up-right",17)}</a>' if eventslug else '')
        cards.append(f'''<article class="past-speaker-card"><div class="past-speaker-card__identity">{speaker_image(sp,'past-speaker-card__avatar')}<div><span class="mini-label">PAST ERS–WVSU PRESENTER</span><h3><a href="{e(internal('speakers/'+sp['slug']+'/'))}">{e(sp.get('name',''))}</a></h3><p>{e(sp.get('position',''))}</p></div></div><div class="past-speaker-card__talk"><span class="mini-label">{e(dat)} {('· '+e(time)) if time else ''}</span><h4>{e(sp.get('past_talk','Previous seminar'))}</h4><p class="talk-summary">{e(detail)}</p></div>{eventlink}</article>''')
    if not cards: cards=['<div class="empty-state"><h3>Past speakers will be listed here as sessions are verified.</h3></div>']
    return f'''{intro_header(c['eyebrow'],c['heading'],c['heading_emphasis'],c['intro'])}
<section class="section"><div class="container">{section_label('01','DOCUMENTED PAST PRESENTATIONS')}<div class="section-heading-row"><h2>{e(c['section_heading'])}</h2><p>{e(c['section_intro'])}</p></div><div class="past-speaker-grid">{''.join(cards)}</div><p class="archive-note">Summaries describe the content and questions discussed, not unpublished empirical results. Presentation materials appear only with permission.</p></div></section>
<section class="section section--sand"><div class="container invitation-band"><div>{section_label('02','YOUR RESEARCH CONVERSATION')}<h2>Share work that could benefit from an economic lens.</h2><p>Economics, data, measurement, and causal inference are at the center of the exchange.</p></div>{button('Propose a seminar',internal('get-involved/#propose'))}</div></section>'''+contact_strip('Past presentations & speaker invitations','Request a correction or inquire about sharing a session.', [('speakers','Past talks & speakers')])

def render_students():
    c = PAGES['students']
    pub = [p for p in STUDENT_PROJECTS if p.get('status')=='published' and p.get('consent_confirmed')]
    pub.sort(key=lambda p:(p.get('sort_order',99),p.get('project_title','')))
    cards=[]
    for p in pub:
        ref=remote_url(p.get('public_url',''))
        link=f'<a class="inline-link" href="{e(ref)}" target="_blank" rel="noopener noreferrer">Explore project {icon("up-right",17)}</a>' if ref else ''
        cards.append(f'''<article class="student-project-card"><span class="mini-label">STUDENT RESEARCH · {e(p.get('year',''))}</span><h3>{e(p.get('project_title',''))}</h3><p class="student-project-card__person">{e(p.get('student_name',''))} {('· '+e(p['program'])) if p.get('program') else ''}</p><p>{e(p.get('summary',''))}</p><p class="student-project-card__method"><strong>Economics / methods angle:</strong> {e(p.get('economics_angle',''))}</p>{link}</article>''')
    if not cards:
        cards=[f'''<div class="student-empty"><div class="student-empty__symbol">{icon('book',52)}</div><span class="mini-label">FEATURED STUDENT WORK</span><h3>{e(c['spotlight_empty_title'])}</h3><p>{e(c['spotlight_empty_text'])}</p>{button('Share a research question',internal('get-involved/#propose'),'gold')}</div>''']
    opportunities=[('01','Research design and questions','Explore how economic reasoning helps turn an idea into a study with clear hypotheses and measurable outcomes.','compass'),('02','Data analysis and methods','Discuss measurement, descriptive analysis, econometric tools, and approaches to identifying causal effects.','chart'),('03','Presentation and development','Practice explaining your work, communicating uncertainty, and preparing research for scholarly review.','speaker')]
    steps=''.join(f'''<article class="student-mentorship-card"><span>{n}</span>{icon(ic,30)}<h3>{e(title)}</h3><p>{e(description)}</p></article>''' for n,title,description,ic in opportunities)
    return f'''{intro_header(c['eyebrow'],c['heading'],c['heading_emphasis'],c['intro'])}
<section class="section student-spotlight-section"><div class="container">{section_label('01','STUDENT RESEARCH SPOTLIGHT')}<div class="section-heading-row"><h2>{e(c['spotlight_title'])}</h2><p>{e(c['spotlight_intro'])}</p></div><div class="student-project-grid">{''.join(cards)}</div><p class="archive-note">Student names, work, and photographs are shared only with appropriate permission; inclusion is subject to review.</p></div></section>
<section class="section section--sand"><div class="container">{section_label('02','MENTORSHIP THROUGH RESEARCH')}<div class="section-heading-row"><h2>{e(c['mentorship_title'])}</h2><p>{e(c['mentorship_intro'])}</p></div><div class="student-mentorship-grid">{steps}</div></div></section>
<section class="section partner-cta"><div class="container partner-cta-grid"><div>{section_label('03','GET STARTED')}<h2>{e(c['closing_title'])}</h2><p>{e(c['closing_text'])}</p></div>{button('Discuss a student project',internal('get-involved/#propose'))}</div></section>'''+contact_strip(
    'Support for emerging researchers', 'Connect about student projects, research spotlight submissions, and mentoring.',
    [('students','Student research spotlight'),('mentorship','Research mentorship')])

def render_archive():
    c=PAGES['archive']
    pub=[x for x in RESOURCES if x.get('status')=='published' and remote_url(x.get('url',''))]
    pub.sort(key=lambda x:x.get('year',''),reverse=True)
    cards=[]
    for x in pub:
        dest=remote_url(x['url'])
        cards.append(f'''<article class="resource-card" data-search-item data-search="{e(x.get('title','')+' '+x.get('description','')+' '+x.get('topic',''))}" data-topic="{e(x.get('type',''))}">
<div class="resource-card__top"><span class="mini-label">{e(x.get('type','RESOURCE'))}</span><span>{e(x.get('year',''))}</span></div><div class="resource-card__icon">{icon('file',27)}</div><h3><a href="{e(dest)}" target="_blank" rel="noopener noreferrer">{e(x.get('title',''))}</a></h3><p>{e(x.get('description',''))}</p><a class="inline-link" href="{e(dest)}" target="_blank" rel="noopener noreferrer">Open resource {icon('up-right',17)}</a></article>''')
    if cards:
        types=sorted({x['type'] for x in pub})
        choices=''.join(f'<option value="{e(t)}">{e(t)}</option>' for t in types)
        controls=f'''<div class="archive-filters"><label class="search-input">{icon('search',18)}<span class="sr-only">Search archive</span><input type="search" placeholder="Search the research archive" data-filter-input aria-label="Search archive"></label><label class="select-wrap"><span class="sr-only">Filter material type</span><select data-filter-select aria-label="Filter material type"><option value="all">All material types</option>{choices}</select></label></div>'''
        catalog=f'{controls}<div class="resource-grid" data-filter-target>{"".join(cards)}</div><p class="filter-empty" data-filter-empty hidden>No matching resources. Adjust your filters.</p>'
    else:
        catalog=f'''<div class="empty-state empty-state--large"><div class="empty-state__icon">{icon('book',31)}</div><div><p class="mini-label">CURATING OUR LIBRARY</p><h3>{e(c['empty_title'])}</h3><p>{e(c['empty_text'])}</p></div></div>'''
    return f'''{intro_header(c['eyebrow'],c['heading'],c['heading_emphasis'],c['intro'])}
<section class="section"><div class="container">{section_label('01','PUBLISHED MATERIALS')}<div class="section-heading-row"><h2>Explore the<br><em>research archive.</em></h2><p>All shared materials remain the intellectual work of their respective authors.</p></div>{catalog}</div></section>
<section class="section section--sand"><div class="container">{section_label('02','WHAT YOU WILL FIND')}<div class="resource-type-grid"><div>{icon('speaker',29)}<h3>Talk slides</h3><p>Selected presentations approved by the speakers for public sharing.</p></div><div>{icon('file',29)}<h3>Papers and briefs</h3><p>Working papers and concise research summaries where permission is granted.</p></div><div>{icon('book',29)}<h3>Learning resources</h3><p>Methods, references, and related resources that support learning and collaboration.</p></div></div></div></section>'''+contact_strip(
    'Questions about research materials?', 'Discuss methods, data, or resource sharing with the research team.',
    [('research','Research & methods')])


def render_newsletter_feature(compact=False):
    # Brevo-managed signup with hosted fallback.
    embed_url=remote_url(SITE.get('mailing_list_embed_url',''))
    parsed=urlparse(embed_url) if embed_url else None
    valid_embed=bool(parsed and parsed.scheme=='https' and parsed.hostname=='c650f365.sibforms.com' and parsed.path.startswith('/v2/serve/'))
    link=remote_url(SITE.get('mailing_list_url',''))
    extra_class=''
    if valid_embed:
        extra_class=' newsletter-feature__action--embed'
        act=(f'<div class="newsletter-embed">'
             f'<iframe class="newsletter-iframe" title="Join the ERS–WVSU Research Community mailing list" '
             f'src="{e(embed_url)}" loading="lazy" scrolling="auto" referrerpolicy="strict-origin-when-cross-origin"></iframe>'
             f'<p class="newsletter-open-link">Having trouble viewing the form? '
             f'<a href="{e(embed_url)}" target="_blank" rel="noopener noreferrer">Open the signup form in a new tab</a>.</p>'
             f'</div>')
        desc=('Receive ERS–WVSU seminar announcements, research opportunities, '
              'collaboration updates, and student mentorship news. '
              'Signups are handled by Brevo; confirm your subscription by email. You may unsubscribe at any time.')
    elif link:
        act=button('Subscribe to ERS updates',link,'gold','up-right')
        desc='Subscribe to receive seminar announcements and research-community updates. You can unsubscribe at any time.'
    else:
        act='<span class="newsletter-pending">Subscription form is being prepared with Brevo.</span>'
        desc='A voluntary mailing list for future seminars and research opportunities is coming soon. No signup data is collected on this website yet.'
    return (f'<section class="section newsletter-feature" id="mailing-list">'
            f'<div class="container newsletter-feature__grid">'
            f'<div>{section_label("07","THE ERS–WVSU MAILING LIST")}<h2>Stay in the<br><em>research conversation.</em></h2><p>{e(desc)}</p></div>'
            f'<div class="newsletter-feature__action{extra_class}">{act}'
            f'<p>Interested in a seminar now? {channel_link("seminars","Write to the seminar team")}.</p>'
            f'</div></div></section>')


def render_involved():
    c=PAGES['get-involved']
    contact=channel_address('contact')
    endpoint=remote_url(SITE.get('formspree_endpoint',''))
    endpoint_ok=bool(re.fullmatch(r'https://formspree\.io/f/[A-Za-z0-9]+',endpoint))
    form=''
    if endpoint_ok:
        form=f'''<form class="research-inquiry" id="research-inquiry" action="{e(endpoint)}" method="POST" data-formspree="true">
  <div class="form-row"><label>Full name <span aria-hidden="true">*</span><input name="name" autocomplete="name" required maxlength="120" placeholder="Your name"></label><label>Email address <span aria-hidden="true">*</span><input name="email" type="email" autocomplete="email" required maxlength="160" placeholder="you@university.edu"></label></div>
  <label>Institution / department<input name="affiliation" maxlength="160" placeholder="University, department, or organization (optional)"></label>
  <label>Type of inquiry <span aria-hidden="true">*</span><select name="inquiry_type" required><option value="">Choose an inquiry type</option><option>Presenting at a seminar</option><option>Speaker invitation or past presentation</option><option>Interdisciplinary research collaboration</option><option>Economic analysis, data or causal inference</option><option>Grant development or funding</option><option>Student research spotlight</option><option>Research mentorship</option><option>Outreach or community engagement</option><option>Join the organizing community</option><option>General question</option></select></label>
  <label>Working title / subject<input name="topic" maxlength="180" placeholder="Short topic or subject (optional)"></label>
  <label>Your question or collaboration idea <span aria-hidden="true">*</span><textarea name="message" required maxlength="1800" rows="5" placeholder="Share a short, nonconfidential description of your question or proposed collaboration"></textarea></label>
  <label class="consent-check"><input type="checkbox" name="permission_to_contact" value="yes" required><span>I understand that ERS–WVSU will use my submission to respond to this inquiry.</span></label>
  <div class="hp-wrap" aria-hidden="true"><label>Leave this field empty<input type="text" name="_gotcha" tabindex="-1" autocomplete="off"></label></div>
  <input type="hidden" name="_subject" value="ERS–WVSU research & seminar inquiry">
  <p class="form-note">{icon('mail',16)} Submit here without opening an email app. Form submissions are processed by Formspree and delivered to the ERS–WVSU contact address. Do not include confidential research methods, student records, or sensitive personal information.</p>
  <button type="submit" class="btn btn--gold" id="inquiry-submit"><span>Submit research inquiry</span>{icon('up-right',18)}</button>
  <p class="form-status" id="inquiry-status" role="status" aria-live="polite"></p>
  </form>'''
    else:
        form=f'<p class="form-note">Our direct submission form is being prepared. In the meantime, contact {channel_link("contact")}. No online submission is collected until the form is enabled.</p>'
    routes=[('01','Propose a focused seminar','Share work where an economic mechanism, data strategy, or causal interpretation could be strengthened.','speaker'),('02','Explore a research collaboration','Find an economics-centered contribution to research originating in another discipline.','users'),('03','Discuss a methods challenge','Bring difficult questions about data, measurement, identification, or inference.','chart'),('04','Get involved with student research','Explore research mentoring, empirical methods, and opportunities to contribute.','book')]
    cards=''.join(f'''<article class="involvement-card"><span>{e(n)}</span>{icon(ic,29)}<h3>{e(t)}</h3><p>{e(d)}</p></article>''' for n,t,d,ic in routes)
    return f'''{intro_header(c['eyebrow'],c['heading'],c['heading_emphasis'],c['intro'])}
<section class="section"><div class="container">{section_label('01','PATHWAYS TO PARTICIPATE')}<div class="section-heading-row"><h2>Many ways<br><em>to contribute.</em></h2><p>Across disciplines, we look for meaningful opportunities to strengthen economics and empirical research.</p></div><div class="involvement-grid">{cards}</div></div></section>
<section class="section section--sand" id="propose"><div class="container propose-grid"><div>{section_label('02','SUBMIT AN INQUIRY')}<h2>{e(c['proposal_title'])}</h2><p class="lead-paragraph">{e(c['proposal_text'])}</p><div class="proposal-steps"><div><span>1</span><p><strong>Identify the question</strong><br>What problem or topic do you want to explore?</p></div><div><span>2</span><p><strong>Connect the economics or data angle</strong><br>Where might methods, measurement or incentives contribute?</p></div><div><span>3</span><p><strong>Suggest a useful next step</strong><br>Seminar, research design conversation, or mentorship?</p></div></div><div class="proposal-context"><strong>Privacy:</strong> Please send only a brief public-safe outline; sensitive or unpublished details can be discussed through an agreed private process.</div></div><div class="contact-panel contact-panel--form" id="contact"><span class="mini-label">CONTACT THE RESEARCH COMMUNITY</span><div class="contact-panel__icon">{icon('mail',31)}</div><h3>{e(c['contact_title'])}</h3><p>{e(c['contact_text'])}</p>{form}<hr><span class="mini-label">DIRECT EMAIL</span>{channel_link('contact')}{'<p>Other ERS–WVSU email contacts are listed below.</p>'}</div></div></section>{email_directory()}{render_newsletter_feature()}'''

def render_about():
    c=PAGES['about']
    principles=''.join(f'''<div class="principle-item"><span>0{i}</span><div><h3>{e(c.get(f'principle_{x}_title',''))}</h3><p>{e(c.get(f'principle_{x}_text',''))}</p></div></div>''' for i,x in enumerate(['one','two','three','four'],1))
    return f'''{intro_header(c['eyebrow'],c['heading'],c['heading_emphasis'],c['intro'])}
<section class="section"><div class="container about-story-grid"><div class="about-story-art"><img src="{e(internal('assets/images/hero-network.svg'))}" alt="Abstract golden connections between research ideas" loading="lazy"><span>INQUIRY <b>·</b> EXCHANGE <b>·</b> IMPACT</span></div><div>{section_label('01','OUR MISSION')}<h2>{e(c['mission_title'])}</h2><p class="lead-paragraph">{e(c['mission_text'])}</p><div class="story-quote">“Rigorous collaboration begins with clarity about the question, the evidence, and each team’s contribution.”</div></div></div></section>
<section class="section section--sand"><div class="container"><div class="section-heading-row">{section_label('02','WHAT GUIDES US')}<h2>Four principles.<br><em>One shared purpose.</em></h2></div><div class="principles-grid">{principles}</div></div></section>
<section class="section origins-section"><div class="container origins-grid"><div>{section_label('03','HOW IT BEGAN')}<h2>{e(c['origin_title'])}</h2></div><div><p class="lead-paragraph">{e(c['origin_text'])}</p><div class="origin-fact"><span>2026</span><p>ERS–WVSU initiative established</p></div>{button('Be part of the story',internal('get-involved/'))}</div></div></section>'''+contact_strip(
    'Reach ERS–WVSU', 'For general correspondence or community and institutional engagement.',
    [('contact','General contact'),('outreach','Outreach & engagement')])


def render_speaker_detail(sp):
    name=sp.get('name','Speaker')
    site_url=remote_url(sp.get('website_url',''))
    # ERS PROFESSIONAL WEBSITE FILTER
    parsed_site = urlparse(site_url) if site_url else None
    site_host = parsed_site.hostname.lower() if parsed_site and parsed_site.hostname else ''
    site_path = parsed_site.path.rstrip('/').lower() if parsed_site else ''
    if sp.get('professional_website_available') is False or site_host == 'directory.wvstateu.edu' or (site_host in ('wvstateu.edu', 'www.wvstateu.edu') and site_path in ('', '/university-directory')):
        site_url = ''

    website=(f'<a class="inline-link" href="{e(site_url)}" target="_blank" rel="noopener noreferrer">{e("View Google Scholar profile" if "scholar.google.com" in site_url else "Visit professional website")} {icon("up-right",16)}</a>' if site_url else '')
    tags=''.join(f'<span class="expertise-tag">{e(t.strip())}</span>' for t in sp.get('expertise','').split(';') if t.strip())
    pub_url=remote_url(sp.get('featured_publication_url',''))
    pub_title=str(sp.get('featured_publication_title','')).strip()
    pub_markup=(f'<aside class="speaker-publication-box"><h3>Selected publication</h3><p><a href="{e(pub_url)}" target="_blank" rel="noopener noreferrer">{e(pub_title or "Read published research")} {icon("up-right",16)}</a></p></aside>') if pub_url else ''
    matching_events=sorted((ev for ev in EVENTS if ev.get('speaker_slug')==sp.get('slug') and future_ev(ev)),key=lambda ev:ev.get('date',''))
    event_markup=(' <p class="speaker-upcoming-link"><a class="inline-link" href="'+e(internal('seminars/'+matching_events[0]['slug']+'/'))+'">Upcoming ERS–WVSU presentation '+icon('up-right',16)+'</a></p>') if matching_events else ''
    talk=''
    if sp.get('past_speaker') and sp.get('past_talk'):
        date=pretty_date(sp['past_talk_date']) if sp.get('past_talk_date') else 'Date forthcoming'
        time=sp.get('past_talk_time','')
        summary=sp.get('past_talk_summary','') or sp.get('past_talk_note','')
        talk=f'''<section class="section section--sand"><div class="container talk-profile"><div>{section_label('02','PAST ERS–WVSU PRESENTATION')}<h2>{e(sp['past_talk'])}</h2><p class="talk-date">{e(date)} {('· '+e(time)) if time else ''}</p></div><p class="lead-paragraph">{e(summary)}</p></div></section>'''
    return f'''<section class="detail-hero"><div class="container"><a class="detail-back" href="{e(internal('speakers/'))}">← All people</a><div class="speaker-detail-grid"><div class="speaker-detail-photo">{speaker_image(sp,'detail-avatar')}</div><div>{eyebrow(sp.get('role','RESEARCH COMMUNITY'),True)}<h1>{e(name)}</h1><p class="detail-subtitle">{e(sp.get('position',''))}<br>{e(sp.get('affiliation',''))}</p></div></div></div></section><section class="section"><div class="container detail-content"><div>{section_label('01','RESEARCH PROFILE')}<h2>About the<br><em>researcher.</em></h2></div><div><p class="lead-paragraph">{e(sp.get('bio','Biography forthcoming.'))}</p><div class="expertise-tags">{tags}</div>{website}{pub_markup}{event_markup}</div></div></section>{talk}'''

def render_event_detail(ev):
    title=ev.get('title','Seminar')
    day=pretty_date(ev.get('date',''))
    time=ev.get('time_label') or ((ev.get('start_time','')+'–'+ev.get('end_time','')) if ev.get('start_time') and ev.get('end_time') else 'Time to be announced')
    speaker=ev.get('speaker_name','Speaker to be announced')
    speaker_link=internal('speakers/'+ev['speaker_slug']+'/') if ev.get('speaker_slug') in {s['slug'] for s in SPEAKERS if s.get('status')=='published'} else ''
    speaker_label=f'<a href="{e(speaker_link)}">{e(speaker)}</a>' if speaker_link else e(speaker)
    links=[]
    if future_ev(ev) and ev.get('start_time') and ev.get('end_time'):
        links.append(button('Add to calendar',internal('seminars/'+ev['slug']+'/event.ics'),'gold','download'))
    reg=remote_url(ev.get('registration_url',''))
    mat=remote_url(ev.get('materials_url',''))
    if reg and future_ev(ev): links.append(button('Registration details',reg,'outline-dark'))
    if mat: links.append(button('View shared materials',mat,'outline-dark'))
    # External publisher pages: do not republish attachment PDFs without permission.
    paper_links=[]
    for key, label in (
        ('paper_commentary_url', 'Read Michael N. Young’s published commentary (2016)'),
        ('paper_original_url', 'Read the original study by McCarthy and colleagues (2016)'),
    ):
        url=remote_url(ev.get(key,''))
        if url:
            paper_links.append(f'<li><a href="{e(url)}" target="_blank" rel="noopener noreferrer">{e(label)} {icon("up-right",16)}</a></li>')
    paper_markup=('<aside class="seminar-reading"><h3>Background reading</h3><p>The two linked articles are optional reading for an interdisciplinary discussion.</p><ul>'+''.join(paper_links)+'</ul></aside>') if paper_links else ''
    audience=ev.get('audience_note','').strip()
    audience_markup=f'<p class="seminar-context"><strong>Who should attend:</strong> {e(audience)}</p>' if audience else ''
    hospitality=ev.get('refreshments_note','').strip()
    hospitality_markup=f'<p class="seminar-context"><strong>At the seminar:</strong> {e(hospitality)}</p>' if hospitality else ''
    action=''.join(links)
    return f'''<section class="detail-hero detail-hero--event"><div class="container"><a class="detail-back" href="{e(internal('seminars/'))}">← All seminars</a>{eyebrow(ev.get('event_type','Research seminar'),True)}<h1>{e(title)}</h1><p class="detail-subtitle">{e(ev.get('topic','Research exchange'))}</p></div></section>
<section class="section"><div class="container event-detail-grid"><div class="event-detail-body">{section_label('01','ABOUT THIS SESSION')}<h2>Research in<br><em>conversation.</em></h2><p class="lead-paragraph">{e(ev.get('abstract','Details will be added soon.'))}</p>{audience_markup}{hospitality_markup}{paper_markup}<div class="event-detail-actions">{action}</div></div>
<aside class="event-facts"><span class="mini-label">SESSION INFORMATION</span><div><span>{icon('calendar',20)} DATE</span><strong>{e(day)}</strong></div><div><span>{icon('clock',20)} TIME</span><strong>{e(time)}</strong></div><div><span>{icon('pin',20)} LOCATION</span><strong>{e(ev.get('location','To be announced'))}</strong></div><div><span>{icon('speaker',20)} PRESENTER</span><strong>{speaker_label}</strong><small>{e(ev.get('speaker_affiliation',''))}</small></div></aside></div></section>'''


def make_appearance_css():
    # Generate safe and human-editable presentation variables from Pages CMS settings.
    sizes={
        'body_font_px': (15,24,18),
        'navigation_font_px': (13,19,15),
        'card_font_px': (14,22,16),
        'small_label_font_px': (11,16,12),
    }
    colors={
        'background_color':'#FCFBF7',
        'secondary_background_color':'#F3F0E7',
        'dark_background_color':'#151A17',
        'accent_color':'#CDAD35',
    }
    values=[]
    for name,(low,high,default) in sizes.items():
        raw=APPEARANCE.get(name,default)
        try: v=int(raw)
        except (ValueError,TypeError): raise ValueError(f'Appearance {name}: enter a number, e.g. {default}')
        if not low<=v<=high: raise ValueError(f'Appearance {name}: choose {low}–{high}px')
        values.append((name.replace('_','-'),f'{v}px'))
    for name,default in colors.items():
        c=str(APPEARANCE.get(name,default)).strip()
        if not re.fullmatch(r'#[0-9A-Fa-f]{6}',c): raise ValueError(f'Appearance {name}: enter a six-digit hex color, e.g. {default}')
        values.append((name.replace('_','-'),c))
    return '/* Generated from content/appearance.json — edit using Pages CMS or a text editor. */\n:root {\n'+''.join(f'  --{name}: {value};\n' for name,value in values)+'}\n'


def write(route, contents):
    path = OUT / route
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(contents, encoding='utf-8')


def ics_escape(value):
    return str(value or '').replace('\\','\\\\').replace('\n','\\n').replace(',','\\,').replace(';','\\;')


def make_ics(ev):
    if not ev.get('date') or not ev.get('start_time') or not ev.get('end_time'): return ''
    date = str(ev['date']).replace('-','')
    start = str(ev['start_time']).replace(':','')+'00'
    end = str(ev['end_time']).replace(':','')+'00'
    if len(start) != 6 or len(end) != 6: return ''
    today=dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    zone=ev.get('timezone','America/New_York') or 'America/New_York'
    return '\r\n'.join([
        'BEGIN:VCALENDAR','VERSION:2.0','PRODID:-//ERS-WVSU//Research Seminar//EN','CALSCALE:GREGORIAN','METHOD:PUBLISH',
        'BEGIN:VEVENT',f'UID:{e(ev["slug"])}@ers-wvsu',f'DTSTAMP:{today}',
        f'DTSTART;TZID={zone}:{date}T{start}',f'DTEND;TZID={zone}:{date}T{end}',
        f'SUMMARY:{ics_escape(ev.get("title"))}',f'LOCATION:{ics_escape(ev.get("location"))}',
        f'DESCRIPTION:{ics_escape(ev.get("abstract"))}','STATUS:CONFIRMED','END:VEVENT','END:VCALENDAR',''])


def render_404():
    return '''<section class="section not-found"><div class="container"><p class="overline">404 · PAGE NOT FOUND</p><h1>That idea went<br><em>somewhere else.</em></h1><p>The page you followed does not exist. The conversation continues on our homepage.</p>'''+button('Return home',internal('index.html'))+'</div></section>'


def validate_records(records, kind):
    slugs=set()
    for row in records:
        slug = row.get('slug','')
        if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*',slug):
            raise ValueError(f"{row.get('_source','unknown')}: slug must contain only lowercase letters, numbers, and hyphens")
        if slug in slugs: raise ValueError(f'{kind}: repeated slug: {slug}')
        slugs.add(slug)
        status=row.get('status')
        allowed={'events':('draft','scheduled','completed'),'speakers':('draft','published'),'resources':('draft','published'),'student-projects':('draft','published')}[kind]
        if status not in allowed: raise ValueError(f"{row['_source']}: invalid status {status!r}")
        if kind == 'events' and status != 'draft':
            if not row.get('date') or not row.get('title') or not row.get('speaker_name'):
                raise ValueError(f"{row['_source']}: published sessions require title, date and speaker")
            dt.date.fromisoformat(row['date'])
        if kind == 'student-projects' and status=='published':
            if not row.get('consent_confirmed'):
                raise ValueError(f"{row['_source']}: student publication requires consent_confirmed=true")
            if not row.get('project_title') or not row.get('student_name'):
                raise ValueError(f"{row['_source']}: student publication requires project_title and student_name")


def build(base_override=None):
    global SITE, BASE, THEMES, CAPABILITIES, PATHWAY, APPEARANCE, EVENTS, SPEAKERS, RESOURCES, STUDENT_PROJECTS, AFFILIATES, COMMUNITY_ROLES, PAGES
    SITE = jload('content/site.json')
    repo = os.environ.get('GITHUB_REPOSITORY','')
    domain = str(SITE.get('custom_domain','')).strip()
    if base_override is not None:
        BASE = '/' + base_override.strip('/') + ('/' if base_override.strip('/') else '')
    elif domain:
        BASE = '/'
    elif repo and '/' in repo:
        BASE = '/' + repo.split('/',1)[1].strip('/') + '/'
    else:
        BASE = '/'
    PAGES = {p.stem:json.loads(p.read_text(encoding='utf-8')) for p in (CONTENT / 'pages').glob('*.json')}
    THEMES = jload('content/themes.json')
    CAPABILITIES = jload('content/capabilities.json')
    PATHWAY = jload('content/pathway.json')
    APPEARANCE = jload('content/appearance.json')
    AFFILIATES = jload('content/affiliates.json')
    COMMUNITY_ROLES = jload('content/community-roles.json')
    EVENTS = collection('events')
    SPEAKERS = collection('speakers')
    RESOURCES = collection('resources')
    STUDENT_PROJECTS = collection('student-projects')
    for rows,key in ((EVENTS,'events'),(SPEAKERS,'speakers'),(RESOURCES,'resources'),(STUDENT_PROJECTS,'student-projects')):
        validate_records(rows,key)
    if OUT.exists(): shutil.rmtree(OUT)
    OUT.mkdir()
    shutil.copytree(ROOT/'public', OUT, dirs_exist_ok=True)
    write('assets/css/appearance.css', make_appearance_css())
    routes={
        'index.html':('home','Home',SITE['meta_description'],render_home()),
        'partnerships/index.html':('partnerships','Research Partnerships',PAGES['partnerships']['intro'],render_partnerships()),
        'seminars/index.html':('seminars','Seminars & Events',PAGES['seminars']['intro'],render_seminars()),
        'speakers/index.html':('speakers','People',PAGES['speakers']['intro'],render_speakers()),
        'past-speakers/index.html':('past','Past Speakers',PAGES['past-speakers']['intro'],render_past_speakers()),
        'students/index.html':('students','Student Research & Mentorship',PAGES['students']['intro'],render_students()),
        'archive/index.html':('archive','Research Archive',PAGES['archive']['intro'],render_archive()),
        'get-involved/index.html':('involved','Get Involved',PAGES['get-involved']['intro'],render_involved()),
        'about/index.html':('about','Our Mission',PAGES['about']['intro'],render_about()),
        '404.html':('none','Page Not Found','The requested page is unavailable.',render_404()),
    }
    for route,(active,title,description,body) in routes.items():
        write(route,shell(active,title,description,body, 'index.html' if route=='index.html' else route.replace('index.html','')))
    for sp in SPEAKERS:
        if sp.get('status')!='published': continue
        route=f'speakers/{sp["slug"]}/index.html'
        write(route,shell('speakers',sp.get('name','Speaker'),sp.get('bio','Researcher profile'),render_speaker_detail(sp),route.replace('index.html','')))
    for ev in EVENTS:
        if not is_published(ev): continue
        route=f'seminars/{ev["slug"]}/index.html'
        write(route,shell('seminars',ev.get('title','Seminar'),ev.get('abstract','Seminar information'),render_event_detail(ev),route.replace('index.html','')))
        if future_ev(ev) and ev.get('start_time') and ev.get('end_time'):
            ics=make_ics(ev)
            if ics: write(f'seminars/{ev["slug"]}/event.ics',ics)
    write('.nojekyll','')
    write('robots.txt','User-agent: *\nAllow: /\n')
    # On a custom domain, GitHub Actions Pages uses the domain configured in Settings;
    # the CNAME file is not needed. Generate site map only after a domain is chosen.
    if domain:
        d=domain.replace('https://','').replace('http://','').strip('/ ')
        locs=['','partnerships/','seminars/','speakers/','past-speakers/','students/','archive/','get-involved/','about/']
        locs += [f'speakers/{s["slug"]}/' for s in SPEAKERS if s.get('status')=='published']
        locs += [f'seminars/{v["slug"]}/' for v in EVENTS if is_published(v)]
        sitemap='<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join(f'<url><loc>https://{e(d)}/{e(p)}</loc></url>' for p in locs)+'</urlset>'
        write('sitemap.xml',sitemap)
        write('robots.txt','User-agent: *\nAllow: /\nSitemap: https://'+d+'/sitemap.xml\n')
    pages = len(list(OUT.rglob('*.html')))
    print(f'Built {pages} HTML pages to {OUT} (BASE_PATH={BASE!r})')
    return pages


if __name__=='__main__':
    parser=argparse.ArgumentParser(description='Build or preview ERS–WVSU')
    parser.add_argument('--base-path',default=None,help='Override URL base, e.g. /ers-wvsu/')
    parser.add_argument('--serve',action='store_true',help='Build and preview locally on http://127.0.0.1:8000')
    args=parser.parse_args()
    build(args.base_path)
    if args.serve:
        import functools
        import http.server
        import webbrowser
        url='http://127.0.0.1:8000/'
        handler=functools.partial(http.server.SimpleHTTPRequestHandler,directory=str(OUT))
        print(f'Preview: {url} (Ctrl+C to stop)')
        webbrowser.open(url)
        http.server.ThreadingHTTPServer(('127.0.0.1',8000),handler).serve_forever()
