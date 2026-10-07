# InspoMint

Pinterest-driven lifestyle magazine. The GitHub repo is still named Folvella; the public brand and canonical host are InspoMint.

## Public site
https://inspomint.com/

Fresh visual guides for food, home, beauty, fashion, DIY and seasonal living. Public pages do not expose trend scores or internal Pinterest research.

## Search
- Canonical host: `https://inspomint.com/`
- Sitemap: https://inspomint.com/sitemap.xml
- RSS: https://inspomint.com/feed.xml
- Google site verification file: `google173a97c5a6d0f5e3.html`
- Legacy GitHub Pages bases (`Trendora`, `Folvella`) redirect through the custom domain and must not be used as canonicals.

## Publishing
See `PUBLISHING.md`. `data/brand.json` is the source for the site name and `siteBase`. `scripts/build.py` emits canonicals, sitemap, RSS and article schema from that base.
