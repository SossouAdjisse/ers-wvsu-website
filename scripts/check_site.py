#!/usr/bin/env python3
"""Validate generated output before publishing (Python standard library only)."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, unquote
import json
import re
import sys

ROOT=Path(__file__).resolve().parent.parent
OUT=ROOT/'dist'
SITE=json.loads((ROOT/'content/site.json').read_text(encoding='utf-8'))

class Scanner(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.links=[]
        self.ids=[]
        self.missing_alt=[]
        self.h1=0
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if a.get('id'): self.ids.append(a['id'])
        if tag=='h1': self.h1+=1
        if tag=='img' and not a.get('alt'): self.missing_alt.append(a.get('src','unknown'))
        for field in ('href','src'):
            if tag in ('a','link','script','img') and a.get(field): self.links.append(a[field])

def main():
    errors=[]
    pages=list(OUT.rglob('*.html'))
    if len(pages)<7: errors.append('Expected at least 7 HTML pages')
    prefix='/'
    home=(OUT/'index.html').read_text(encoding='utf-8')
    match=re.search(r'<link rel="stylesheet" href="([^"]+assets/css/site.css)"',home)
    if match: prefix=match.group(1).rsplit('assets/css/site.css',1)[0]
    for page in pages:
        scan=Scanner(); scan.feed(page.read_text(encoding='utf-8'))
        if scan.h1!=1: errors.append(f'{page.relative_to(OUT)}: expected 1 h1, got {scan.h1}')
        if len(scan.ids)!=len(set(scan.ids)): errors.append(f'{page.relative_to(OUT)}: repeated element id')
        for alt in scan.missing_alt: errors.append(f'{page.relative_to(OUT)}: image without alt: {alt}')
        for link in scan.links:
            p=urlsplit(link)
            if p.scheme or link.startswith('//') or link.startswith('#') or p.path=='': continue
            path=unquote(p.path)
            if not path.startswith(prefix):
                errors.append(f'{page.relative_to(OUT)}: link outside site base: {link}')
                continue
            rel=path[len(prefix):].lstrip('/')
            candidate=OUT/rel
            if path.endswith('/') or not candidate.suffix: candidate=candidate/'index.html'
            if not candidate.is_file(): errors.append(f'{page.relative_to(OUT)}: missing file: {link}')
    if errors:
        for item in errors: print('ERROR:',item)
        sys.exit(1)
    print(f'PASS: {len(pages)} HTML pages, internal paths, images, and unique page headings verified (base {prefix!r}).')

if __name__=='__main__': main()
