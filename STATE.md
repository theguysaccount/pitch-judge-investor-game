# STATE: 2026-10-25

**Before this repo:** one June 2023 note ("Recorded pitches, ask someone to say whether they would invest. Then have this person manage a fund." … "Where does this data exist?"). No code or data.

**Settled from the note:** outcome-labelled pitch data does exist in public. Startups and TV pitches with documented outcomes cover it, written in our own words and sourced. Recorded pitch videos are not needed, which avoids founder-consent and copyright problems.

**Works now:**
- Live game: daily (deterministic by UTC date, five a day, a full cycle before any repeat) and practice (ten at random).
- 76 case-file pages, a spoiler deck page, 17 score share pages with share images, an embed widget, an about page.
- Weekly deploy, weekly self-test with source link checks, keep-alive, CI. 15 Python and 5 Node tests.
- All 76 source URLs resolve. The anonymisation check passes on every pitch.

**Known gaps:**
- No cross-player leaderboard: there is no server. Scores compare through share grids.
- Famous companies are guessable from their pitch, as expected.
- Analytics are off until a GoatCounter key is set; there is no custom domain.
- The deck grows only through the quarterly routine.

**Worth reusing:** `site/assets/core.js` (deterministic daily selection with no repeats within a cycle, plus share-grid text) for any daily game.
