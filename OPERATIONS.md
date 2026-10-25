# OPERATIONS

## Automated jobs

### `deploy.yml`: build and publish
**When:** pushes to `main` touching `judge/`, `data/`, `site/` or `scripts/`; weekly on Mondays at 08:11 UTC; or by hand.

**Steps:**
1. Python tests, including deck validation with sources, tiers and the anonymisation check, and the build tests.
2. Node tests of `core.js`.
3. The build (`python -m judge.site`).
4. Share images (`scripts/og.py`; the default card is used if Chrome fails).
5. Pages deploy.
6. IndexNow submission of every indexable URL (never fails the run).
7. Keep-alive on scheduled runs.

**Fails safe:** an invalid deck, a failed test or a failed build stops before deploying, and the last good deploy stays live. GitHub emails the repository owner on failure.

### `selftest.yml`: weekly check (Thursdays 06:29 UTC)
- Tests on `main`.
- `scripts/health.py` checks that 10 live URLs answer and that `deck.json` loads with 50+ pitches. The embed page and its scripts are among those URLs.
- It also checks that every cited source resolves. Bot walls (401/403/429) are not counted. The run fails if more than 10% (minimum 3) of sources are broken; fewer is listed in the run summary.
- Then keep-alive.

### `keepalive.yml`: called by every scheduled workflow
- Re-enables every workflow through the API.
- Pushes a `.github/heartbeat` commit after 40 quiet days. GitHub disables schedules after 60 days without activity.

### `ci.yml`: every push and pull request
Python 3.9 and 3.12, plus the Node tests.

## The daily game needs no job
`site/assets/core.js` picks today's five from the UTC date and the deck. Daily #1 is 2026-10-25. Each cycle of 15 days deals every pitch once, then the deck reshuffles. Adding pitches changes future cycles.

## Scheduled Claude routine (quarterly; set up once by a human)

Actions has no model API key, so researching and writing new pitches is a Claude Code routine. Schedule it in Claude Code on the 1st of January, April, July and October, in a checkout of this repo, with this prompt:

> In ~/code/pitch-judge-investor-game (git pull first):
> 1. Read `data/backlog.json`. For each unresolved candidate, check public sources (Wikipedia and the reporting it cites) for a resolution that meets a tier definition in `judge/data.py`. Breakout means a $1B+ acquisition, IPO value or private valuation. Success means acquired, or a lasting business with sizeable sales. Bust means shut down, bankrupt or a fire sale.
> 2. For each resolved candidate, add a pitch to `data/pitches.json`:
>    - the year and stage at the time it was pitched;
>    - an 80-420 character anonymised pitch in our own words, using only facts the source supports;
>    - 1-3 facts, the outcome, the outcome text, the outcome year and what investors did at the time;
>    - https sources.
>    Never name founders, and never use show logos or video.
> 3. Re-check five existing pitches at random against their sources and fix anything that changed.
> 4. Keep busts between 35% and 60% of the deck.
> 5. Review open issues labelled `correction`, fix what is sourced and close each with a comment.
> 6. Run `python3 -m unittest discover -s tests -t .` and `node --test tests/js.test.mjs`, then commit and push. The push deploys. Do not post anywhere.

Without the routine the game keeps running indefinitely on the current 76 pitches, cycling every 15 days.

## What to watch

| Signal | Where | Healthy |
|---|---|---|
| Runs | Actions tab; failure emails | Weekly deploy and self-test green |
| Source links | Self-test run summary | 0 broken (a few are fine; fix within a quarter) |
| Engagement | GoatCounter once the key is set: `game_start`, `call`, `game_complete` (activation), `share`, `case_call` | Completion rate over 60% of starts |
| Corrections | Issues labelled `correction` | Resolved quarterly |

## Keys Jack can turn later

| Key | Why | Exact steps |
|---|---|---|
| **Custom domain** | Brand and a root robots.txt | LAUNCH.md §5 (`play.silicontank.com` needs one CNAME) |
| **Money: support link** | First revenue without leaving GitHub Pages' non-commercial terms | Create a GitHub Sponsors profile or another support page, set the repository variable `PJ_SPONSOR_URL` to it, and run `gh workflow run deploy.yml`. A "Support the game" link appears in the footer. Ads need an ad-network account and hosting off Pages |
| **Analytics** | Measure `game_complete` and shares | Create a GoatCounter site, set `PJ_GOATCOUNTER=https://<code>.goatcounter.com/count` and redeploy. It is cookieless and honours DNT and GPC |
| **Global leaderboard / scout program** | Find top judges, as the original note intended | Needs accounts, a database, a privacy policy and hosting off Pages. Also needs a decision on whether Persist recruits from it |
| **Live pitch decks** | Startupathon or VideoAsk pitch videos with outcomes resolved later | Needs each founder's written consent first; then add a `consent` field and a separate deck |
| **Quarterly Claude routine** | Grow the deck as outcomes resolve | Set up once, as above |
