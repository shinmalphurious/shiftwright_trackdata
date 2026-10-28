import unittest

from src.pipelines.validate_track_knowledge import validate


def markers(*turns, direction_known=True):
    return {"direction_known": direction_known, "turns": [{"label": l, "lap_pct": p} for l, p in turns]}


def kinds(issues):
    return sorted(i["issue"] for i in issues)


class Validate(unittest.TestCase):

    def test_clean_layout_with_wrap_at_the_line_has_no_issues(self):
        self.assertEqual(validate(1, markers(("T1", 0.95), ("T2", 0.03), ("T3", 0.2)), [], {}), [])

    def test_zandvoort_style_markers(self):
        m = markers(("T1", 0.73), ("T1", 0.72), ("T1", 0.09), ("T2", 0.16), ("T10", 0.59), ("T12", 0.76))
        corners = [{"name": "Hans Ernst Bocht", "start_pct": 0.70, "end_pct": 0.77}]
        issues = validate(485, m, corners, {})
        self.assertIn("duplicate_turn_id", kinds(issues))
        self.assertIn("named_corner_repeats_label", kinds(issues))
        missing = next(i for i in issues if i["issue"] == "missing_turn_number")
        self.assertIn("T11", missing["turn_ids"])

    def test_turn_out_of_order(self):
        issues = validate(1, markers(("T1", 0.1), ("T2", 0.5), ("T3", 0.3), ("T4", 0.6)), [], {})
        self.assertEqual(kinds(issues), ["non_sequential_order"])

    def test_aliases(self):
        config = {"layouts": {"1": {"T1": ["banking", "tarzan"], "T2": ["tarzan"], "T9": ["nowhere"]}}}
        issues = validate(1, markers(("T1", 0.1), ("T2", 0.2)), [], config)
        self.assertEqual(kinds(issues), ["alias_collision", "ambiguous_alias", "invalid_reference"])


if __name__ == "__main__":
    unittest.main()
