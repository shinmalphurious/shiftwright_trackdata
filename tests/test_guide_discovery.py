import unittest
from unittest import mock

import src.pipelines.run_guide_discovery as discovery
from src.pipelines.run_guide_discovery import discover, judge, planned_queries, queries, venue_match, venue_profile
from src.shared.iracing_tracks import load_layouts
from src.shared.track_names import aliases, normalize, repair

MEXICO_GP = 572


def video(title, duration=600, description=""):
    return {"id": "x", "title": title, "duration": duration, "description": description}


class Names(unittest.TestCase):
    def test_double_encoded_name_is_repaired(self):
        self.assertEqual(repair("AutÃ³dromo Hermanos RodrÃ­guez"), "Autódromo Hermanos Rodríguez")
        self.assertEqual(repair("Circuito de Jerez - Ã\u0081ngel Nieto"), "Circuito de Jerez - Ángel Nieto")

    def test_clean_text_is_left_alone(self):
        for text in ("Autódromo Hermanos Rodríguez", "Nürburgring", "Spa-Francorchamps", ""):
            self.assertEqual(repair(text), text)

    def test_normalize_ignores_case_accents_and_spacing(self):
        self.assertEqual(normalize("Autódromo  Hermanos Rodríguez"), normalize("autodromo hermanos-rodriguez"))
        self.assertEqual(normalize("  Lånkebanen (Hell RX) "), "lankebanen hell rx")

    def test_metadata_has_no_garbled_names(self):
        for info in load_layouts().values():
            self.assertNotRegex(info["name"], "[ÃÂ­]", info["name"])
        self.assertEqual(load_layouts()[MEXICO_GP]["venue"], "Autódromo Hermanos Rodríguez")

    def test_aliases_found_by_any_spelling(self):
        self.assertIn("Mexico City", aliases("Autodromo Hermanos Rodriguez")[0])
        self.assertIn("Mexico City", aliases("AutÃ³dromo Hermanos RodrÃ­guez")[0])


class MexicoCity(unittest.TestCase):
    def setUp(self):
        self.info = load_layouts()[MEXICO_GP]
        self.profile = venue_profile(self.info)

    def test_queries_use_clean_name_and_aliases(self):
        q = queries(self.info)
        self.assertEqual(q[0], "iracing Autodromo Hermanos Rodriguez - Grand Prix track guide")
        self.assertIn("iracing Mexico City track guide", q)
        self.assertIn("iracing Mexico GP track guide", q)
        self.assertTrue(all(text.isascii() for text in q))
        self.assertEqual(len(q), len({normalize(text) for text in q}))

    def test_titles_naming_the_venue_differently_are_accepted(self):
        for title in ("Mexico City GT3 Guide", "Mexico GP Track Guide", "Autodromo Hermanos Rodriguez Guide",
                      "HOW TO DO AUTÓDROMO HERMANOS RODRÍGUEZ IN iRacing | GT3 Track Guide & Tips",
                      "iRacing F3 Mexico City Guide 1:57.1 Dallara F3 Hermanez Rodriguez Track Guide",
                      "HOW TO DO MEXICO IN iRacing | GT3 Track Guide & Tips"):
            verdict = judge(video(title), self.info, self.profile, {})
            self.assertIsNone(verdict["reason"], title)

    def test_confidence_reflects_how_the_venue_is_named(self):
        full, _ = venue_match("Autodromo Hermanos Rodriguez Guide", self.profile)
        alias, _ = venue_match("Mexico City GT3 Guide", self.profile)
        misspelt, _ = venue_match("Hermanez Rodriguez guide", self.profile)
        weak, _ = venue_match("Mexico track guide", self.profile)
        self.assertEqual(full, 1.0)
        self.assertEqual(alias, 1.0)
        self.assertTrue(0.5 <= weak < misspelt < alias)

    def test_rejections_say_why(self):
        cases = {"Monza Track Guide": "venue not in title",
                 "Mexico City GT3 hotlap 1:40": "no guide words in title",
                 "Mexico City GT3 setup guide": "setup or hardware video"}
        for title, reason in cases.items():
            self.assertEqual(judge(video(title), self.info, self.profile, {})["reason"], reason, title)
        self.assertEqual(judge(video("Mexico City Track Guide", duration=30), self.info, self.profile, {})["reason"],
                         "too short")


class OtherVenues(unittest.TestCase):
    """Matches the old exact rules allowed must keep working."""

    def test_joined_and_short_names(self):
        layouts = load_layouts()
        for track_id, title in ((225, "iRacing Track Guides 2018 - Autoclub"),
                                (232, "ARCA IRP Qualifying Guide | iRacing")):
            info = layouts[track_id]
            self.assertIsNone(judge(video(title), info, venue_profile(info), {})["reason"], title)


class FakeYouTube:
    """Answers every search with the same videos and counts the searches."""

    def __init__(self, videos):
        self.videos, self.searches = videos, 0

    def extract_info(self, query, download=False):
        self.searches += 1
        return {"entries": [dict(v) for v in self.videos]}


def yt(vid, title, duration=600):
    return {"id": vid, "title": title, "duration": duration, "description": "iRacing"}


class Refresh(unittest.TestCase):
    def setUp(self):
        self.info = load_layouts()[MEXICO_GP]
        patcher = mock.patch.object(discovery.time, "sleep")
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_query_kinds(self):
        kinds = dict(planned_queries(self.info))
        self.assertEqual(kinds["iracing Mexico City track guide"], "alias")
        self.assertEqual(kinds["iracing Autodromo Hermanos Rodriguez track guide"], "repaired")
        zandvoort = next(i for i in load_layouts().values() if i["venue"] == "Circuit Zandvoort")
        self.assertEqual({k for _, k in planned_queries(zandvoort)}, {"name"})

    def test_previous_selection_is_kept_and_new_videos_fill_up(self):
        better = [yt(f"new{i}", f"iRacing Mexico City GP Track Guide {i}") for i in range(12)]
        previous = [{"video_id": "old", "title": "Mexico guide", "car": "gr86"}]
        selected, records, diag, _ = discover(FakeYouTube(better), self.info, {}, previous, {})
        ids = [v["video_id"] for v in selected]
        self.assertIn("old", ids)
        self.assertEqual(len(ids), discovery.TARGET)
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(next(v for v in selected if v["video_id"] == "old")["car"], "gr86")
        self.assertEqual(diag["kept_previous"], 1)
        self.assertEqual(diag["new_selected"], discovery.TARGET - 1)

    def test_previously_rejected_video_is_re_evaluated(self):
        ledger = {"x": {"title": "Autodromo Hermanos Rodriguez Track Guide", "duration": 600,
                        "status": "rejected", "reason": "venue not in title", "first_seen": "2026-01-01"}}
        _, records, diag, _ = discover(FakeYouTube([]), self.info, {}, [], ledger)
        self.assertIsNone(records["x"]["reason"])
        self.assertEqual(records["x"]["status"], "selected")
        self.assertEqual(records["x"]["first_seen"], "2026-01-01")
        self.assertEqual(diag["new_candidates"], 0)

    def test_search_metadata_updates_existing_video(self):
        previous = [{"video_id": "v", "title": "Mexico City Track Guide", "car": "general"}]
        fresh = [dict(yt("v", "Mexico City Track Guide (updated)"), channel="Coach")]
        selected, records, _, _ = discover(FakeYouTube(fresh), self.info, {}, previous, {})
        self.assertEqual(selected[0]["channel"], "Coach")
        self.assertEqual(records["v"]["title"], "Mexico City Track Guide (updated)")
        self.assertTrue(records["v"]["found_by"])

    def test_reupload_of_a_kept_video_is_not_selected_twice(self):
        previous = [{"video_id": "orig", "title": "Mexico City Track Guide", "car": "general"}]
        copy = [yt("copy", "Mexico City Track Guide")]
        selected, records, _, _ = discover(FakeYouTube(copy), self.info, {}, previous, {})
        self.assertEqual([v["video_id"] for v in selected], ["orig"])
        self.assertEqual(records["copy"]["reason"], "duplicate title")

    def test_alias_queries_always_run_and_repeats_come_from_cache(self):
        good = [yt(f"g{i}", f"iRacing Autodromo Hermanos Rodriguez Track Guide GR86 {i}") for i in range(12)]
        youtube, cache = FakeYouTube(good), {}
        _, _, diag, _ = discover(youtube, self.info, {}, [], {}, cache)
        aliases = sum(1 for _, k in planned_queries(self.info) if k == "alias")
        self.assertGreaterEqual(diag["queries_run"], aliases + 2)
        searches = youtube.searches
        _, _, diag, _ = discover(youtube, self.info, {}, [], {}, cache)
        self.assertEqual(youtube.searches, searches)
        self.assertEqual(diag["queries_cached"], diag["queries_run"])


if __name__ == "__main__":
    unittest.main()
