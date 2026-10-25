# Would You Fund It? (repo: pitch-judge-investor-game)

**Play:** https://theguysaccount.github.io/pitch-judge-investor-game/ · **Every pitch (spoilers):** [/deck/](https://theguysaccount.github.io/pitch-judge-investor-game/deck/) · **Screens:** [docs/screens](docs/screens/)

A daily startup-judgment game. You read real pitches as investors saw them, with the company name hidden: the year, the stage, the traction and the ask. You decide **invest** or **pass**, then see what actually happened and its source. Each outcome is one of three:
- 🦄 **Breakout:** $1B+ via acquisition, IPO or private valuation;
- ✅ **Success:** acquired or a lasting business below $1B;
- 💥 **Bust:** shut down, bankrupt or sold off for a fraction.

- **Daily:** the same five pitches for everyone, by UTC date, with a Wordle-style share grid (🦄 ✅ ❌).
- **Practice:** ten at random, no limit.
- **Case files:** one page per pitch (76), titled for the searches people make ("Would you have funded Doorbot?").
- **TV pitches:** you are scored against what the show's investors actually did.
- **Share cards** for every score; an embeddable "today's pitch" widget.

No accounts, no cookies, nothing uploaded: results stay in the browser.

## The deck

`data/pitches.json`: 76 pitches (1997-2019), with 24 breakouts, 18 successes and 34 busts. 11 come from a televised pitch show. Every pitch:
- is written in our own words from facts that were public at the time;
- has an outcome sourced to a public page (mostly Wikipedia, which cites the reporting);
- passes an automatic check that the visible pitch does not contain the company's distinctive name.

Busts make up 45% of the deck, so "always invest" scores badly.

## How it runs (no human in the loop)

| Job | Workflow | When | Fails safe because |
|---|---|---|---|
| Validate the deck, test, build, render share images, deploy to Pages, ping IndexNow | `deploy.yml` | on content or code pushes; weekly Monday 08:11 UTC; by hand | an invalid deck, a failed test or a failed build stops before deploy, and the last good deploy stays live |
| Live pages, deck, embed, and every cited source link | `selftest.yml` | weekly Thursday 06:29 UTC | read-only |
| Keep schedules alive | `keepalive.yml` | called by every scheduled workflow | runs even if the caller fails |
| Tests (Python 3.9/3.12 + Node) | `ci.yml` | every push | n/a |

New pitches and newly resolved outcomes come from a quarterly Claude routine (see [OPERATIONS.md](OPERATIONS.md)). The daily game needs no rebuild: the browser picks today's five from the date.

## Layout

```
judge/data.py     load + validate the deck (sources, tiers, anonymisation)
judge/site.py     static site generator (game pages, case files, deck, score pages, embed, sitemap)
site/assets/      core.js (daily selection, scoring, share text), game.js, embed.js, app.js, style.css
data/             pitches.json (the deck), backlog.json (candidates awaiting outcomes)
scripts/          og.py (share images), indexnow.py, health.py (live + link check), screens.mjs
tests/            unittest suites + Node tests for core.js
```

## Run, test, deploy

```bash
python3 -m judge.site                    # build dist/
python3 scripts/og.py dist               # optional: share images with local Chrome
python3 -m http.server 4751 --directory dist
python3 -m unittest discover -s tests -t .
node --test tests/js.test.mjs
```

Deploys run from `deploy.yml` on push to `main`, or with `gh workflow run deploy.yml`.

## Licence

Code MIT; deck text CC BY 4.0. Company names identify the companies described. A game, not investment advice.
