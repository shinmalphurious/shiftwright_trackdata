import unittest

from src.knowledge.claims import CLAIMS
from src.knowledge.consensus import load_config, score

CONFIG = load_config()
RESEARCH = [{"source": "ai:test", "confidence": 0.99}, {"source": "geometry", "confidence": 0.6}]
NONE = {"confirm": [], "contradict": []}


def ev(research=RESEARCH, confirm=0, contradict=0, telemetry=None, laps=10, variants=()):
    return {"research": research,
            "transcript": {"confirm": [{"video_id": f"v{i}"} for i in range(confirm)],
                           "contradict": [{"video_id": f"x{i}"} for i in range(contradict)]},
            "telemetry": {"result": telemetry, "laps": laps} if telemetry else None,
            "variants": list(variants)}


class Consensus(unittest.TestCase):

    def test_research_alone_never_promotes(self):
        result = score(ev(), CONFIG)
        self.assertEqual(result["status"], "pending")
        self.assertLessEqual(result["confidence"]["research"], CONFIG["research_prior_cap"])

    def test_telemetry_or_transcript_can_approve(self):
        self.assertEqual(score(ev(telemetry="confirm"), CONFIG)["status"], "validated")
        self.assertEqual(score(ev(confirm=2), CONFIG)["status"], "validated")

    def test_telemetry_contradiction_outweighs_research_and_transcripts(self):
        result = score(ev(confirm=2, telemetry="contradict"), CONFIG)
        self.assertEqual(result["status"], "rejected")

    def test_transcript_contradictions_reject(self):
        self.assertEqual(score(ev(contradict=2), CONFIG)["status"], "rejected")

    def test_variant_evidence_counts_scaled_by_inheritance(self):
        strong = score(ev(variants=[{"result": "confirm", "inheritance_confidence": 1.0}]), CONFIG)
        self.assertEqual(strong["status"], "validated")
        weak = score(ev(research=[{"source": "geometry", "confidence": 0.45}],
                        variants=[{"result": "confirm", "inheritance_confidence": 0.9}]), CONFIG)
        self.assertEqual(weak["status"], "pending")

    def test_layer_confidences_are_kept_apart(self):
        c = score(ev(confirm=1, telemetry="confirm"), CONFIG)["confidence"]
        self.assertGreater(c["telemetry"], c["transcript"])
        self.assertGreater(c["consensus"], c["telemetry"])


class Claims(unittest.TestCase):

    def test_heavy_braking_reads_brake_pressure_not_throttle(self):
        test = CLAIMS["heavy_braking"]["transcript"]
        self.assertEqual(test({"braking": "lamp post on left, 80%"}), "confirm")
        self.assertIsNone(test({"braking": "lift slightly", "exit": "100% throttle"}))
        self.assertEqual(test({"line": "absolutely flat through here"}), "contradict")

    def test_flat_out(self):
        test = CLAIMS["flat_out"]["transcript"]
        self.assertEqual(test({"line": "flat out"}), "confirm")
        self.assertEqual(test({"braking": "50% at the board", "line": "then flat"}), "contradict")

    def test_telemetry_tests(self):
        heavy = CLAIMS["heavy_braking"]["telemetry"]
        self.assertEqual(heavy({"peak_brake": 0.85, "speed_drop": 0.5}), "confirm")
        self.assertEqual(heavy({"peak_brake": 0.0, "speed_drop": 0.02}), "contradict")
        self.assertIsNone(CLAIMS["chicane"]["telemetry"])


if __name__ == "__main__":
    unittest.main()
