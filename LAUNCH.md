# LAUNCH: machine-driven

The game launches and spreads without anyone posting, emailing or hosting anything.

## 1. What's live

- **Game:** https://theguysaccount.github.io/pitch-judge-investor-game/ (daily) and `/practice/`
- **Case files:** `/pitch/<slug>/` (76 pages); the spoiler index is at `/deck/`
- **Share pages:** `/score/<n>-of-5/` and `/score/<n>-of-10/`, each with its own share image (not indexed)
- **Widget:** `/embed/daily/` (the iframe code is on the about page)
- **Data:** `/data/deck.json` (CC BY 4.0)

## 2. How a deploy happens

1. `deploy.yml` runs on pushes to `main` that change the deck or code, weekly (Monday 08:11 UTC) to refresh the sitemap and share images, or with `gh workflow run deploy.yml`.
2. It runs the tests, including deck validation and the anonymisation check, then the game-logic tests.
3. It builds, renders share images, deploys to Pages and submits IndexNow.

The daily challenge needs no deploy: browsers pick today's five from the UTC date.

## 3. How people find it (machine channels only)

| Channel | What is in place |
|---|---|
| Share loop | The end-of-round Wordle-style grid (`Would You Fund It? #12 4/5` 🦄✅❌✅✅) with native share, copy and X buttons, linking to a score page whose share image shows the score |
| Search | 76 case files titled "Would you have funded <Company>? The <year> pitch and what happened"; the home page targets "startup investing game"; practice targets "startup investing quiz"; the deck targets "startups that boomed and busted" |
| Structured data | `WebSite` and `Game` on home, `Article` with citations on case files, `Dataset` on the deck |
| IndexNow | Every deploy submits all indexable URLs |
| Embed | An "Today's pitch" iframe for blogs, newsletters and course sites, linking back to the game |
| GitHub | Public repo, description, topics, open deck data |

Search terms the pages are built to answer:
- `would you invest quiz`, `startup investing game`
- `guess the startup`, `shark tank quiz`
- `<company> what happened`, `<company> shark tank update`
- `failed startups examples`, `famous startup failures`

## 4. The first 14 days (automatic)

| Day | Automation | What to look at (optional) |
|---|---|---|
| 0 | Deploy and IndexNow submission | Actions green |
| Daily | A new daily set at 00:00 UTC (#1 = 2026-10-25), with no deploy needed | The home page shows the next number |
| Mon | Weekly rebuild: fresh sitemap and share images | Run summary |
| Thu | Self-test: pages, deck, embed and 76 source links | Run summary |

## 5. Production domain (needs Jack; nothing is blocked)

1. **play.silicontank.com.** `silicontank.com` is owned (Namecheap) and also hosts the startup-scoreboard idea.
2. **wouldyoufundit.org.** Unregistered per WHOIS on 2026-10-25, about $10/yr. Needs Jack's OK to spend.
3. **fundorpass.com.** Unregistered per WHOIS on 2026-10-25. Backup. (`wouldyoufundit.com` and `pitchjudge.com` are registered to others.)

Steps for option 1:
1. At Namecheap (silicontank.com), add `CNAME play theguysaccount.github.io.`
2. Set the repository variables `PJ_CUSTOM_DOMAIN=play.silicontank.com` and `PJ_BASE_URL=https://play.silicontank.com`.
3. Run `gh workflow run deploy.yml`.
4. In Settings, then Pages, confirm the domain and enforce HTTPS.

For an apex domain (option 2), use the GitHub Pages A/AAAA records: `185.199.108.153`, `185.199.109.153`, `185.199.110.153`, `185.199.111.153` and `2606:50c0:8000::153` to `2606:50c0:8003::153`. Add `CNAME www theguysaccount.github.io.`, then steps 2-4.
