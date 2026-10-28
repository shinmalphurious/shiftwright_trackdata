"""Tests for the deterministic corner enrichment stages (python -m unittest discover tests)."""
import unittest

from src.pipelines.enrich_corner_assignments import (
    alias_stage, alias_table, assign, brackets, clean_turns, derived, fixed_points, lap_position_stage,
    load_settings, locate, norm_words, sequence_stage)

SETTINGS = load_settings({"minimum_confidence": 0.75, "max_passes": 3, "confidence_decay_per_pass": 0.02})
TURNS = [("T1", 0.10), ("T2", 0.20), ("T3", 0.30), ("T4", 0.40), ("T5", 0.50)]


def note(t, corner=None, confidence=1.0, **fields):
    n = {"_t": t, "corner_id": None, "status": "unassigned", "evidence": {}, **fields}
    if corner:
        assign(n, corner, confidence, "explicit", {})
        n["_pct"] = dict(TURNS)[corner]
    return n


def run_pass(notes, enrichment_pass=1, lm=None, segments=()):
    for n in notes:
        if n["corner_id"]:
            n["_pct"] = dict(TURNS)[n["corner_id"]]
    found = brackets(notes, fixed_points(notes, list(segments)))
    for n in notes:
        n["_bracket"] = found.get(id(n))
    placed = sequence_stage(notes, TURNS, lm, SETTINGS, enrichment_pass)
    for n in notes:
        if not n["corner_id"] and n["_bracket"]:
            hit = lap_position_stage(n, TURNS, lm, SETTINGS, enrichment_pass)
            if hit and hit[1] >= SETTINGS["minimum_confidence"]:
                assign(n, hit[0], hit[1], "lap_position", hit[2], enrichment_pass)
                placed += 1
    return placed


class CleanTurns(unittest.TestCase):

    def test_duplicate_label_keeps_the_marker_in_lap_order(self):
        pack = {"turns": [{"label": "T1", "lap_pct": 0.73}, {"label": "T1", "lap_pct": 0.08},
                          {"label": "T2", "lap_pct": 0.15}, {"label": "T12", "lap_pct": 0.75}]}
        turns, dropped = clean_turns(pack)
        self.assertEqual(turns, [("T1", 0.08), ("T2", 0.15), ("T12", 0.75)])
        self.assertEqual(dropped, [("T1", 0.73)])


class Aliases(unittest.TestCase):
    PACK = {"named_corners": [{"name": "Tarzanbocht", "labels": ["T1"]},
                              {"name": "Arie Luyendijk Bocht", "labels": ["T5"]},
                              {"name": "Esses", "labels": ["T2", "T3"]}]}

    def table(self, layout=None):
        config = {"default_confidence": 0.98, "layouts": {"7": layout or {}},
                  "global": {"last": {"aliases": ["final corner"], "confidence": 0.9}}}
        return alias_table(7, self.PACK, config, [l for l, _ in TURNS])

    def test_pack_names_give_spoken_variants(self):
        table = self.table()
        self.assertEqual(table["tarzan"], ("T1", 0.98))
        self.assertEqual(table["arie luyendyk"], ("T5", 0.98))
        self.assertEqual(table["final corner"], ("T5", 0.9))
        self.assertNotIn("esses", table)  # a name for two turns places nothing

    def test_alias_claimed_by_two_corners_is_ignored(self):
        self.assertNotIn("banking", self.table({"T3": ["banking"], "T5": ["banking"]}))

    def test_alias_must_be_in_the_transcript_and_unambiguous(self):
        table = self.table()
        segments = [(0, "braking hard"), (3, "into tarzan now"), (6, "back on the gas")]
        self.assertEqual(alias_stage({"_line": 0}, segments, table)[0], "T1")
        self.assertIsNone(alias_stage({"_line": 0}, [(0, "braking hard"), (3, "the hairpin")], table))
        self.assertIsNone(alias_stage({"_line": 0}, [(0, "from tarzan to the final corner")], table))


class Sequence(unittest.TestCase):

    def test_single_corner_between_two_named_corners(self):
        notes = [note(10, "T1"), note(15, line="late apex"), note(20, "T3")]
        run_pass(notes)
        self.assertEqual((notes[1]["corner_id"], notes[1]["assignment_method"]), ("T2", "sequence_match"))
        self.assertEqual(notes[1]["confidence"], 0.93)
        self.assertEqual(notes[1]["enrichment_pass"], 1)

    def test_two_corners_between_without_telemetry_is_left_to_lap_position(self):
        notes = [note(10, "T1"), note(15, braking="70%"), note(30, "T4")]
        run_pass(notes)
        self.assertNotEqual(notes[1].get("assignment_method"), "sequence_match")

    def test_telemetry_matches_braking_notes_to_braking_corners_in_order(self):
        lm = {"laps": 3, "braking_turns": {"T1", "T2", "T3"}, "elapsed": []}
        notes = [note(10, "T1"), note(14, braking="50%"), note(18, braking="80%"), note(30, "T5")]
        run_pass(notes, lm=lm)
        self.assertEqual([n["corner_id"] for n in notes[1:3]], ["T2", "T3"])
        self.assertEqual(notes[1]["assignment_method"], "telemetry_match")

    def test_telemetry_count_mismatch_assigns_nothing_by_telemetry(self):
        lm = {"laps": 3, "braking_turns": {"T2", "T3", "T4"}, "elapsed": []}
        notes = [note(10, "T1"), note(14, braking="50%"), note(30, "T5")]
        run_pass(notes, lm=lm)
        self.assertNotEqual(notes[1].get("assignment_method"), "telemetry_match")

    def test_start_finish_mention_brackets_the_first_corners(self):
        notes = [note(14, line="flat"), note(20, "T2")]
        run_pass(notes, segments=[(8, "down the main straight")])
        self.assertEqual((notes[0]["corner_id"], notes[0]["evidence"]["after"]), ("T1", "start/finish"))

    def test_new_lap_between_does_not_bracket(self):
        notes = [note(10, "T5"), note(15, line="x"), note(20, "T1")]
        found = brackets(notes, fixed_points(notes, []))
        self.assertNotIn(id(notes[1]), found)


class MultiPass(unittest.TestCase):

    def test_placements_become_fixed_points_for_the_next_pass(self):
        # T1 . . T4: pass 1 places the note next to T3 by lap position, pass 2 the other by sequence
        # note "a" sits too far from T2 for lap position alone (0.63 < 0.75)
        notes = [note(0, "T1"), note(13, line="a"), note(20, line="b"), note(30, "T4")]
        self.assertEqual(run_pass(notes, 1), 1)
        self.assertIsNone(notes[1]["corner_id"])
        self.assertEqual((notes[2]["corner_id"], notes[2]["enrichment_pass"]), ("T3", 1))
        self.assertEqual(run_pass(notes, 2), 1)
        self.assertEqual((notes[1]["corner_id"], notes[1]["assignment_method"], notes[1]["enrichment_pass"]),
                         ("T2", "sequence_match", 2))
        self.assertLess(notes[1]["confidence"], notes[2]["confidence"])

    def test_confidence_never_exceeds_the_fixed_points_and_decays_per_pass(self):
        self.assertAlmostEqual(derived(SETTINGS, "sequence_match", 1.0, 1), 0.93)
        self.assertAlmostEqual(derived(SETTINGS, "sequence_match", 0.9, 2), 0.93 * 0.9 - 0.02)
        self.assertLessEqual(derived(SETTINGS, "telemetry_match", 0.8, 1), 0.8)

    def test_weak_fixed_points_place_nothing(self):
        notes = [note(10, "T1", confidence=0.78), note(15, line="late apex"), note(20, "T3")]
        run_pass(notes)
        self.assertIsNone(notes[1]["corner_id"])  # 0.93 * 0.78 = 0.73 < 0.75


class LapPosition(unittest.TestCase):

    def test_confidence_falls_away_from_the_corner(self):
        notes = [note(0, "T1"), note(10, line="x"), note(13, line="y"), note(20, "T5")]
        found = brackets(notes, fixed_points(notes, []))
        for n in notes:
            n["_bracket"] = found.get(id(n))
        near = lap_position_stage(notes[1], TURNS, None, SETTINGS, 1)
        between = lap_position_stage(notes[2], TURNS, None, SETTINGS, 1)
        self.assertEqual(near[0], "T3")
        self.assertAlmostEqual(near[1], 0.9)
        self.assertLess(between[1], 0.75)


class Locating(unittest.TestCase):
    CFG = SETTINGS["locate"]
    SEGMENTS = [(0, "welcome back to the channel"), (3, "so we come down the hill"),
                (6, "breaking at the hundred board about 70%"), (9, "down to third gear"),
                (12, "lots of talk here about the weather"), (15, "and more talk about setups"),
                (18, "turn in at the cone and hit the apex curb"), (21, "talking about tyres now"),
                (24, "still talking about tyres"), (27, "and the weather again"),
                (30, "full throttle all the way onto the back straight"), (33, "nothing else"),
                (36, "more chat"), (39, "again chat"), (42, "never run wide over the sausage kerb")]

    def test_caption_spelling_is_evened_out(self):
        self.assertIn("brake", norm_words("breaking"))
        self.assertIn("curb", norm_words("kerbs"))

    def test_note_spread_over_the_passage_is_found_by_its_fields(self):
        source = {"braking": "brake at the hundred board, 70%",
                  "line": "turn in at the cone, hit the apex curb",
                  "exit": "full throttle all the way onto the back straight",
                  "mistakes": "never run wide over the sausage kerb"}
        where = locate(source, self.SEGMENTS, 0, 50, self.CFG)
        self.assertEqual(where["how"], "per_field")
        self.assertEqual(self.SEGMENTS[where["line"]][0], 6)  # placed at the braking point

    def test_reworded_note_stays_unlocated(self):
        source = {"line": "maintain consistent rhythm, avoid overdriving"}
        where = locate(source, self.SEGMENTS, 0, 30, self.CFG)
        self.assertIsNone(where["line"])
        self.assertEqual(where["issue"], "paraphrased")

    def test_search_stays_inside_the_passage(self):
        source = {"line": "turn in at the cone and hit the apex curb"}
        self.assertIsNone(locate(source, self.SEGMENTS, 0, 10, dict(self.CFG, context_seconds=0))["line"])


if __name__ == "__main__":
    unittest.main()
