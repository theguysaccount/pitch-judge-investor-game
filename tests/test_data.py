import collections
import unittest

from judge import data


class DeckTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.deck = data.load()

    def test_deck_validates(self):
        self.assertEqual(data.validate(self.deck), [])

    def test_enough_pitches_for_two_weeks_of_dailies(self):
        self.assertGreaterEqual(len(self.deck), 70)

    def test_outcomes_are_balanced_so_always_invest_does_not_win(self):
        c = collections.Counter(p["outcome"] for p in self.deck)
        bust_share = c["bust"] / float(len(self.deck))
        self.assertTrue(0.35 <= bust_share <= 0.6, bust_share)
        self.assertGreaterEqual(c["breakout"], 10)
        self.assertGreaterEqual(c["success"], 10)

    def test_tv_pitches_record_what_the_investors_did(self):
        tv = [p for p in self.deck if p["kind"] == "tv"]
        self.assertGreaterEqual(len(tv), 8)
        self.assertTrue(all(p["pros_call"] in ("invest", "pass") for p in tv))

    def test_anonymisation_check_catches_leaks(self):
        p = dict(self.deck[0])
        p["pitch"] = p["pitch"] + " Doorbot is great."
        self.assertIn("Doorbot", data.leaks(p))

    def test_headlines_are_unique(self):
        heads = [p["headline"] for p in self.deck]
        self.assertEqual(len(heads), len(set(heads)))

    def test_every_outcome_is_sourced(self):
        for p in self.deck:
            self.assertTrue(p["sources"], p["slug"])
            for s in p["sources"]:
                self.assertTrue(s["url"].startswith("https://"), p["slug"])


if __name__ == "__main__":
    unittest.main()
