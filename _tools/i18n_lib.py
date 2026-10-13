import re, glob, os, json
from bs4 import BeautifulSoup, NavigableString, Comment
PAGES=[f for f in sorted(glob.glob('*.html'))]
INLINE={'a','strong','em','span','br','small','code','b','i'}
SKIP={'script','style','svg','noscript'}
ATTRS=['alt','aria-label','placeholder','title']
META_KEYS={'description','og:title','og:description','twitter:title','twitter:description','og:image:alt','twitter:image:alt'}

def has_tag_children(el): return any(getattr(c,'name',None) for c in el.children)
def has_text(el): return any(isinstance(c,NavigableString) and not isinstance(c,Comment) and c.strip() for c in el.children)
def inner(el): return ''.join(str(c) for c in el.children).strip()

def walk(soup, fn):
    """call fn(kind, node_or_el, key) for each translatable unit"""
    if soup.title and soup.title.string: fn('title',soup.title,soup.title.string.strip())
    for m in soup.find_all('meta'):
        k=m.get('name') or m.get('property')
        if k in META_KEYS and m.get('content'): fn('meta',m,m['content'].strip())
    body=soup.body
    def rec(el):
        if el.name in SKIP: return
        for a in ATTRS:
            if el.get(a) and el.name not in ('html',) and not (a=='title' and el.name=='title'): fn('attr',(el,a),el[a].strip())
        if el.name=='option' and el.get('value')=='' : pass
        if has_text(el):
            if not has_tag_children(el):
                fn('text',el,el.get_text().strip()); return
            if all(c.name in INLINE for c in el.children if getattr(c,'name',None)):
                fn('html',el,inner(el)); return
            for c in list(el.children):
                if isinstance(c,NavigableString) and not isinstance(c,Comment) and c.strip(): fn('node',c,str(c).strip())
                elif getattr(c,'name',None): rec(c)
            return
        for c in el.children:
            if getattr(c,'name',None): rec(c)
    rec(body)

def collect():
    seen={}
    for p in PAGES:
        soup=BeautifulSoup(open(p,encoding='utf-8').read(),'html.parser')
        def fn(kind,node,key):
            if key and re.search(r'[A-Za-z]{2}',re.sub(r'<[^>]+>','',key)): seen.setdefault(key,[]).append(p)
        walk(soup,fn)
    return seen
