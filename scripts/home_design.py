"""Render the discovery homepage from real published editorial content."""
import html, re, json
from pathlib import Path
from site_config import ROOT, BASE
from urllib.parse import urlencode

esc = lambda value: html.escape(str(value), quote=True)
slug = lambda value: re.sub(r'[^a-z0-9]+', '-', value.lower()).strip('-')

def pin_url(post, media=None, description=None):
    media = media or post.get('pinCover') or post['cover']
    if not media.startswith('https://'): media = BASE + media
    query = urlencode({'url': BASE + post['slug'] + '/', 'media': media, 'description': description or post.get('pinDescription') or post['excerpt']})
    return 'https://www.pinterest.com/pin/create/button/?' + query

def pin_link(post):
    query = pin_url(post).split('?', 1)[1]
    return '<a class="pinBubble" href="https://www.pinterest.com/pin/create/button/?' + esc(query) + '" target="_blank" rel="noopener noreferrer" aria-label="Save ' + esc(post['title']) + ' to Pinterest"><svg class="pinterestSvg" viewBox="0 0 24 24" aria-hidden="true"><path d="M12 2a10 10 0 0 0-3.6 19.3c0-.8.1-1.8.3-2.6l1.3-5.5s-.3-.7-.3-1.6c0-1.5.9-2.6 2-2.6.9 0 1.4.7 1.4 1.5 0 .9-.6 2.3-.9 3.6-.3 1.1.5 2 1.6 2 1.9 0 3.4-2 3.4-5 0-2.6-1.9-4.4-4.5-4.4-3.1 0-4.9 2.3-4.9 4.7 0 .9.4 1.9.8 2.5l-.3 1.2c-1.4-.6-2.2-2.6-2.2-4.2 0-3.4 2.5-6.6 7.2-6.6 3.8 0 6.7 2.7 6.7 6.3 0 3.7-2.4 6.8-5.7 6.8-1.1 0-2.1-.6-2.5-1.2l-.7 2.6c-.2 1-.9 2.1-1.4 2.9A10 10 0 1 0 12 2z"/></svg></a>'

def render_home(old, posts, head, footer, img, cards):
    category_covers = json.loads((ROOT / 'data/category-covers.json').read_text())
    categories = list(category_covers)
    preferred = ['minimal-habit-tracker-ideas', 'deer-print-nail-ideas', 'pleated-skirt-fall-outfits']
    featured = [next((p for p in posts if p['slug'] == s), posts[i]) for i, s in enumerate(preferred)]
    intro = '<section class="discoveryIntro shell"><p class="introKicker">A LITTLE INSPIRATION, EVERY DAY</p><h1>Find something you love.</h1><p>Beautiful ideas to make, wear, try and keep.</p></section>'
    circles = '<section class="categoryStrip" aria-label="Explore topics"><div class="shell categoryRow" id="categoryRow">' + ''.join('<a href="category/' + slug(c) + '/">' + img(category_covers[c], '', False) + '<span>' + esc(c) + '</span></a>' for c in categories) + '</div></section>'
    picks = '<section class="shell featuredSection" aria-labelledby="featuredTitle"><div class="sectionHead"><h2 id="featuredTitle">The Folvella edit</h2><a class="textLink" href="#fresh">Explore all ideas <span aria-hidden="true">↗</span></a></div><div id="heroMount" class="featuredGrid">' + cards(featured) + '</div></section>'
    collections = '<section class="collectionSection" id="collections"><div class="shell"><div class="sectionHead"><div><h2>Your next inspiration</h2><p>Start with a collection that feels like you.</p></div><a class="textLink" href="categories/">All collections ↗</a></div><div class="collectionGrid">'
    for c, title, description in [('Home Decor', 'Make yourself at home', 'Warm corners, thoughtful details.'), ('Beauty & Nails', 'Nail ideas to keep', 'Little details, a fresh perspective.'), ('Food & Drinks', 'Your home café', 'Recipes for a slower morning.')]:
        items = [p for p in posts if p['category'] == c][:3]
        if not items: continue
        collections += '<a class="collectionCard" href="category/' + slug(c) + '/"><div class="collectionImages">' + ''.join(img(p['cover'], p['coverAlt']) for p in items) + '</div><h3>' + esc(title) + '</h3><p>' + esc(description) + '</p><span class="collectionArrow" aria-hidden="true">↗</span></a>'
    collections += '</div></div></section>'
    fresh = '<section class="section" id="fresh"><div class="shell"><div class="sectionHead"><div><h2>More to love</h2><p>Useful, visual guides worth reading and saving.</p></div></div><div class="filters" id="filters"><button class="active" aria-pressed="true" data-filter="all">All ideas</button>' + ''.join('<button aria-pressed="false" data-filter="' + esc(c) + '">' + esc(c) + '</button>' for c in categories) + '</div><p id="searchStatus" role="status" aria-live="polite"></p><div class="ideaGrid" id="ideaGrid">' + cards(posts) + '</div><div class="emptyState" id="emptyState" hidden><h2>No matching ideas yet.</h2><p>Try a different search or category.</p></div></div></section>'
    header = '<a class="skipLink" href="#main">Skip to content</a><header class="topbar"><div class="shell nav"><a class="brand" href="index.html">Folvella</a><nav aria-label="Main navigation"><a href="#fresh">Discover</a><a href="fall-ideas/">Fall edit</a><a href="#collections">Collections</a></nav><form class="search" id="siteSearch" role="search"><svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="10" cy="10" r="6"/><path d="m15 15 6 6"/></svg><input aria-label="Search article titles and categories" id="searchInput" type="search" placeholder="Find your next idea…"><button type="submit" aria-label="Search">↗</button></form></div></header>'
    season = '<section class="shell seasonalBanner"><div><p class="introKicker">THE OCTOBER EDIT</p><h2>A little cozy. A little creative.</h2><p>Warm corners, home café recipes and small projects for a slower season.</p></div><a class="textLink" href="fall-ideas/">Explore the fall edit ↗</a></section>'
    return head + '<body data-page="home">' + header + '<main id="main">' + intro + circles + picks + season + collections + fresh + '</main>' + footer() + '<script src="assets/app.js?v=20261004-complete" defer></script></body></html>'
