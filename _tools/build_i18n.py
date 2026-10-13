#!/usr/bin/env python3
"""Generate /zh /ja /fr pages from the English master pages.
Run from the repo root:  python3 _tools/build_i18n.py
English pages are only decorated (hreflang, language switcher, css link, form language field)."""
import sys, os, re, json, importlib.util
from bs4 import BeautifulSoup, NavigableString
sys.path.insert(0, os.path.dirname(__file__))
import i18n_lib as L
SITE='https://transwindcn.com'
LANGS={'zh':dict(html='zh-CN',og='zh_CN',label='中文',group='语言'),
       'ja':dict(html='ja',og='ja_JP',label='日本語',group='言語'),
       'fr':dict(html='fr',og='fr_FR',label='FR',group='Langue'),
       'en':dict(html='en',og='en_US',label='EN',group='Language')}
ORDER=['en','zh','ja','fr']
PAGES=[p for p in L.PAGES if p!='404.html']
HERE=os.path.join(os.path.dirname(__file__),'i18n')
en=json.load(open(os.path.join(HERE,'en.json'),encoding='utf-8'))
key2id={v:k for k,v in en.items()}

def load(lang):
    spec=importlib.util.spec_from_file_location(lang,os.path.join(HERE,lang+'.py'))
    m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m.T

def segs(s,fn):
    return ''.join(p if p.startswith('<') else fn(p) for p in re.split(r'(<[^>]+>)',s))
def punct(lang,s):
    if lang=='ja':
        return segs(s,lambda t:t.replace('?','？').replace('(','（').replace(')','）').replace(':','：'))
    if lang=='fr':
        def f(t):
            t=re.sub(r'(?<=\S) ?([?!;])',lambda m:' '+m.group(1),t)
            t=re.sub(r'(?<=[^\s:]) ?:(?=\s|$)',' :',t)
            t=t.replace('« ','« ').replace(' »',' »')
            return t
        return segs(s,f)
    return s

def prefix(lang,href):
    if not href.startswith('/') or href.startswith('//') or href.startswith('/assets') or re.match(r'/[0-9a-f]{32}\.txt',href): return href
    if href=='/index.html': return f'/{lang}/'
    return f'/{lang}'+href

def translate(src,lang,T):
    soup=BeautifulSoup(src,'html.parser')
    miss=[]
    def get(key):
        i=key2id.get(key)
        if i is None or i not in T:
            if re.search(r'[A-Za-z]{2}',re.sub(r'<[^>]+>','',key)): miss.append(key)
            return None
        return punct(lang,T[i])
    def fn(kind,node,key):
        t=get(key)
        if t is None: return
        if kind=='title': node.string=t
        elif kind=='meta': node['content']=re.sub(r'<[^>]+>','',t)
        elif kind=='attr': node[0][node[1]]=re.sub(r'<[^>]+>','',t)
        elif kind=='text': node.clear(); node.append(NavigableString(t))
        elif kind=='html':
            node.clear()
            for c in list(BeautifulSoup(t,'html.parser').contents): node.append(c)
        elif kind=='node': node.replace_with(NavigableString(' '+t if False else t))
    L.walk(soup,fn)
    for a in soup.find_all(href=True): a['href']=prefix(lang,a['href'])
    return str(soup),miss

def url(lang,page):
    if lang=='en': return SITE+('/' if page=='index.html' else '/'+page)
    return SITE+f'/{lang}/'+('' if page=='index.html' else page)
def path(lang,page):
    if lang=='en': return '/'+page if page!='index.html' else '/index.html'
    return f'/{lang}/'+('' if page=='index.html' else page)

def decorate(h,lang,page):
    meta=LANGS[lang]
    h=re.sub(r'<html[^>]*>',f'<html lang="{meta["html"]}">',h,count=1)
    h=re.sub(r'<link[^>]*hreflang=[^>]*>','',h)
    h=re.sub(r'<meta[^>]*property="og:locale"[^>]*>','',h)
    h=re.sub(r'<div[^>]*class="lang-switch"[^>]*>.*?</div>','',h,flags=re.S)
    h=re.sub(r'<input[^>]*name="page_language"[^>]*>','',h)
    can=url(lang,page)
    h=re.sub(r'<link[^>]*rel="canonical"[^>]*>',f'<link rel="canonical" href="{can}">',h)
    h=re.sub(r'<meta[^>]*property="og:url"[^>]*>',f'<meta property="og:url" content="{can}">',h)
    alts=''.join(f'<link rel="alternate" hreflang="{LANGS[l]["html"]}" href="{url(l,page)}">' for l in ORDER)
    alts+=f'<link rel="alternate" hreflang="x-default" href="{url("en",page)}">'
    h=re.sub(r'(<link rel="canonical"[^>]*>)',lambda m:m.group(1)+alts,h,count=1)
    h=re.sub(r'(<meta[^>]*property="og:site_name"[^>]*>)',lambda m:m.group(1)+f'<meta property="og:locale" content="{meta["og"]}">',h,count=1)
    if 'assets/css/i18n.css' not in h:
        h=h.replace('</head>','<link rel="stylesheet" href="/assets/css/i18n.css"></head>',1)
    sw=f'<div class="lang-switch" role="group" aria-label="{meta["group"]}">'+''.join(
        f'<a href="{path(l,page)}" lang="{LANGS[l]["html"]}" hreflang="{LANGS[l]["html"]}"'+(' aria-current="true"' if l==lang else '')+f'>{LANGS[l]["label"]}</a>' for l in ORDER)+'</div>'
    h=h.replace('</nav>',sw+'</nav>',1)
    h=re.sub(r'(<form\b[^>]*>)',lambda m:m.group(1)+f'<input type="hidden" name="page_language" value="{lang}">',h)
    return h

def main():
    langs=['zh','ja','fr']
    tr={l:load(l) for l in langs}
    allmiss={}
    for p in PAGES:
        src=open(p,encoding='utf-8').read()
        # English master: strip previous decoration only through decorate()
        open(p,'w',encoding='utf-8').write(decorate(src,'en',p))
        master=open(p,encoding='utf-8').read()
        for l in langs:
            out,miss=translate(master,l,tr[l])
            if miss: allmiss.setdefault(l,set()).update(miss)
            out=decorate(out,l,p)
            os.makedirs(l,exist_ok=True)
            open(f'{l}/{p}','w',encoding='utf-8').write(out)
    # sitemap
    rows=['<?xml version="1.0" encoding="UTF-8"?>','<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">']
    for p in PAGES:
        for l in ORDER:
            rows.append('  <url>\n    <loc>%s</loc>\n'%url(l,p)+''.join(f'    <xhtml:link rel="alternate" hreflang="{LANGS[a]["html"]}" href="{url(a,p)}"/>\n' for a in ORDER)+f'    <xhtml:link rel="alternate" hreflang="x-default" href="{url("en",p)}"/>\n  </url>')
    rows.append('</urlset>')
    open('sitemap.xml','w',encoding='utf-8').write('\n'.join(rows)+'\n')
    for l,m in allmiss.items(): print('MISSING',l,len(m),list(m)[:5])
    print('done',len(PAGES),'pages x',len(langs))
main()
