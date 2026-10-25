# DECISIONS

**D1: written pitches from public facts, not recorded videos.**
- The note asks where outcome-labelled pitch data exists. Recorded pitch videos raise consent and copyright issues and rarely have outcomes attached.
- Public companies with documented outcomes, written up in our own words with sources, give the same judgment test legally and immediately.

**D2: a daily game, not a fund.**
- "Have the best judge manage a fund" would trigger Investment Advisers Act and securities rules, so it is cut.
- The machine version is the judgment game itself, with a daily format for retention and sharing.

**D3: three outcome tiers with stated thresholds.**
- Breakout ($1B+ acquisition, IPO value or private valuation), Success (an exit or lasting business below that), Bust (shut down, bankrupt, fire sale).
- Mixed outcomes (IPO then bankruptcy, such as WeWork, Blue Apron and Casper) are left out until a tier rule for early investors is decided. They are listed in `data/backlog.json`.

**D4: a call is right if you invest in a breakout or success, or pass on a bust.**
- A simple, explainable score that works in a share grid.
- Busts are 45% of the deck, so blind investing scores worse than judgment.

**D5: names hidden, with a machine check.**
- `judge.data.leaks()` fails the build if a distinctive name token appears in the headline, pitch or facts.
- Famous companies remain guessable, which is part of the fun.

**D6: the daily set comes from the UTC date in the browser (`core.js`).**
- Everyone gets the same five without a server.
- Each cycle uses every pitch once before reshuffling.
- Adding pitches changes future cycles, which is acceptable.

**D7: no server, no accounts.**
- Results live in localStorage, and comparisons happen through share grids and score pages.
- A global leaderboard is a key for later and needs non-Pages hosting.

**D8: TV pitches use factual references only.**
- The show is named as a fact ("appeared on Shark Tank" only where the source says it). No logos, video or show branding, and founders are not named in the game text.

**D9: unsourced claims removed.**
- Every pitch-time detail that could not be confirmed in the cited source was cut before publishing, for example Airbnb's cereal boxes and specific asks.
- Companies whose outcome Wikipedia could not settle were dropped: Color Labs, Path, LivingSocial, Digg, MoviePass, Fyre, Washio and Beepi.

## Questions for Jack (none block v1)
1. Is this the same game as Benchshots or CODEVX, and should they share a brand?
2. Use Persist's Startupathon pitch videos in a future "live" deck? Each founder's written consent is needed first.
3. Domain: `play.silicontank.com` (owned) or register `wouldyoufundit.org` (unregistered on 2026-10-25). See LAUNCH.md.
4. Scout program: would Persist want to recruit top players? That needs accounts and a privacy policy, off GitHub Pages.
