#!/usr/bin/env python3
"""Build the English-only Guides section from _tools/guides/*.json.
Run from the repo root AFTER python3 _tools/build_i18n.py (guides copy the versioned head from documents.html).
Each guide JSON: slug, title, description, date (YYYY-MM-DD), minutes, image, image_alt, lede, body_html."""
import os, re, json, glob, html

SITE = 'https://transwindcn.com'
HERE = os.path.join(os.path.dirname(__file__), 'guides')

def shell(src_page='documents.html'):
    d = open(src_page, encoding='utf-8').read()
    head, rest = d.split('<main id="main">', 1)
    foot = rest.split('</main>', 1)[1]
    return head, foot

def page(head, foot, title, desc, url, main, ld=None):
    h = re.sub(r'<title>.*?</title>', f'<title>{html.escape(title)}</title>', head, count=1)
    for name in ('description',):
        h = re.sub(rf'<meta name="{name}" content="[^"]*">', f'<meta name="{name}" content="{html.escape(desc)}">', h)
    for prop, val in (('og:title', title), ('twitter:title', title), ('og:description', desc), ('twitter:description', desc)):
        h = re.sub(rf'(<meta (?:property|name)="{prop}" content=")[^"]*(">)', lambda m: m.group(1) + html.escape(val) + m.group(2), h)
    h = re.sub(r'<meta property="og:type" content="[^"]*">', '<meta property="og:type" content="article">' if ld else '<meta property="og:type" content="website">', h)
    h = re.sub(r'<link rel="canonical"[^>]*>', f'<link rel="canonical" href="{url}">', h)
    h = re.sub(r'<meta property="og:url"[^>]*>', f'<meta property="og:url" content="{url}">', h)
    h = re.sub(r'<link rel="alternate" hreflang[^>]*>', '', h)
    h = h.replace(f'<link rel="canonical" href="{url}">', f'<link rel="canonical" href="{url}"><link rel="alternate" hreflang="en" href="{url}">', 1)
    if ld:
        h = h.replace('</head>', '<script type="application/ld+json">' + json.dumps(ld, ensure_ascii=False, separators=(',', ':')) + '</script></head>', 1)
    # language switcher: English only, other languages go to their homepages
    sw = ('<div class="lang-switch" role="group" aria-label="Language"><a href="/guides/" lang="en" hreflang="en" aria-current="true">EN</a>'
          '<a href="/zh/" lang="zh-CN" hreflang="zh-CN">中文</a><a href="/ja/" lang="ja" hreflang="ja">日本語</a><a href="/fr/" lang="fr" hreflang="fr">FR</a></div>')
    h = re.sub(r'<div class="lang-switch".*?</div>', sw, h, count=1, flags=re.S)
    return h + '<main id="main">' + main + '</main>' + foot

def fmt_date(d):
    y, m, dd = d.split('-')
    months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    return f'{int(dd)} {months[int(m) - 1]} {y}'

def main():
    head, foot = shell()
    guides = sorted((json.load(open(f, encoding='utf-8')) for f in glob.glob(os.path.join(HERE, '*.json'))), key=lambda g: g['date'], reverse=True)
    os.makedirs('guides', exist_ok=True)
    for g in guides:
        url = f"{SITE}/guides/{g['slug']}.html"
        ld = {"@context": "https://schema.org", "@type": "Article", "headline": g['title'], "description": g['description'],
              "datePublished": g['date'], "dateModified": g.get('updated', g['date']), "inLanguage": "en",
              "image": f"{SITE}/assets/images/photos/{g['image']}", "mainEntityOfPage": url,
              "author": {"@type": "Organization", "name": "TransWind", "url": SITE + '/'},
              "publisher": {"@type": "Organization", "name": "TransWind", "logo": {"@type": "ImageObject", "url": SITE + '/assets/logo/brand-assets/TransWind-logo-red.svg'}}}
        main = ('<section class="page-hero has-photo"><figure class="hero-photo"><img src="/assets/images/photos/' + g['image'] + '" alt="' + html.escape(g['image_alt']) + '" loading="lazy"></figure>'
                '<div class="wrap"><div class="hero-copy"><nav class="breadcrumb" aria-label="Breadcrumb"><a href="/guides/">Guides</a><span aria-current="page">' + html.escape(g['short']) + '</span></nav>'
                '<h1>' + html.escape(g['title']) + '</h1><p class="lede">' + html.escape(g['lede']) + '</p>'
                '<p class="article-meta">' + fmt_date(g['date']) + ' · ' + str(g['minutes']) + ' min read · TransWind</p></div></div></section>'
                '<section class="section white"><div class="wrap copy article-body">' + g['body_html'] + '</div></section>'
                '<section class="section"><div class="wrap"><div class="article-cta"><div><h2>' + html.escape(g['cta_title']) + '</h2><p>' + html.escape(g['cta_text']) + '</p></div>'
                '<a class="button" href="' + g['cta_href'] + '">' + html.escape(g['cta_button']) + '</a></div>'
                '<p class="subpage-links"><a class="text-link" href="/guides/">More guides</a></p></div></section>')
        open(f"guides/{g['slug']}.html", 'w', encoding='utf-8').write(page(head, foot, g['title'] + ' | TransWind', g['description'], url, main, ld))
    cards = ''.join('<a class="card card-link" href="/guides/' + g['slug'] + '.html"><span class="kicker">' + fmt_date(g['date']) + '</span><h3>' + html.escape(g['title']) + '</h3><p>' + html.escape(g['description']) + '</p><span class="more">Read the guide →</span></a>' for g in guides)
    main = ('<section class="page-hero has-photo"><figure class="hero-photo"><img src="/assets/images/photos/optics-valley-sky-train-blue.jpg" alt="A suspended sky train passing over a flowering meadow at sunset in Wuhan" loading="lazy"></figure>'
            '<div class="wrap"><div class="hero-copy"><span class="eyebrow">Guides</span><h1>Practical guides for working in China</h1>'
            '<p class="lede">Short, practical answers for companies and individuals working with Chinese suppliers, documents and institutions.</p></div></div></section>'
            '<section class="section"><div class="wrap"><h2>What these guides cover</h2>'
            '<p style="max-width:760px">Each guide answers one practical question for overseas companies, families and institutions working with China, from preparing a visit to Chinese suppliers to getting documents accepted. They are written from the work we do with clients in China, in plain English.</p>'
            '<p class="subpage-links"><a class="text-link" href="/business-visit-interpreting.html">Business visit interpreting day packages</a><a class="text-link" href="/translation-pricing.html">Translation and interpreting rates</a><a class="text-link" href="/documents.html">Common documents we translate</a></p></div></section>'
            '<section class="section white"><div class="wrap"><div class="grid three guide-list">' + cards + '</div></div></section>')
    open('guides/index.html', 'w', encoding='utf-8').write(page(head, foot, 'Guides | TransWind', 'Practical guides for companies and individuals working with Chinese suppliers, documents and institutions.', SITE + '/guides/', main))
    print('built', len(guides), 'guides')

main()
