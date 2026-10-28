"""Weighted evidence consensus for one claim about one corner.

Evidence is combined as odds, not averaged. The research confidence (capped) is the prior; each
piece of evidence multiplies the odds by its likelihood ratio from config/consensus.json:
telemetry counts most, then transcripts (once per video), then variants (the same corner at
another layout, scaled by how certainly it is the same corner), then extra research sources.
A claim is promoted only with at least one piece of transcript, telemetry or variant evidence
confirming it, so research alone can never make knowledge authoritative.
"""
import json

from src.shared.paths import REPO_ROOT

CONFIG = REPO_ROOT / "config" / "consensus.json"


def load_config():
    return json.loads(CONFIG.read_text(encoding="utf-8"))


def _p(odds):
    return odds / (1 + odds)


def score(evidence, config):
    """evidence: {"research": [{source, confidence}], "transcript": {"confirm": [..], "contradict": [..]},
    "telemetry": {"result", "laps"} or None, "variants": [{"result", "inheritance_confidence", ...}]}
    Returns {confidence: {research, transcript, telemetry, variants, consensus}, status, reason, counts}."""
    lr = config["likelihood_ratios"]
    research = evidence.get("research") or []
    prior = min(max((r["confidence"] for r in research), default=config["prior_without_research"]),
                config["research_prior_cap"])
    odds = prior / (1 - prior)
    extra = min(max(len({r["source"] for r in research}) - 1, 0), 2)
    odds *= lr["extra_research_source"] ** extra

    transcript = evidence.get("transcript") or {"confirm": [], "contradict": []}
    confirms = min(len(transcript["confirm"]), lr["max_transcript_videos"])
    contradicts = min(len(transcript["contradict"]), lr["max_transcript_videos"])
    t_factor = lr["transcript_confirm"] ** confirms * lr["transcript_contradict"] ** contradicts

    telemetry = evidence.get("telemetry") or {}
    result, laps = telemetry.get("result"), telemetry.get("laps", 0)
    single = laps < 2
    m_factor = 1.0
    if result == "confirm":
        m_factor = lr["telemetry_confirm_single_lap"] if single else lr["telemetry_confirm"]
    elif result == "contradict":
        m_factor = lr["telemetry_contradict_single_lap"] if single else lr["telemetry_contradict"]

    v_factor, used = 1.0, 0
    for v in sorted(evidence.get("variants") or [], key=lambda v: -v["inheritance_confidence"]):
        if used >= lr["max_variant_sources"] or v["result"] not in ("confirm", "contradict"):
            continue
        base = lr["variant_confirm"] if v["result"] == "confirm" else lr["variant_contradict"]
        v_factor *= base ** v["inheritance_confidence"]
        used += 1

    posterior = _p(odds * t_factor * m_factor * v_factor)
    layer = lambda f, present: round(_p(f), 3) if present else None
    confidence = {
        "research": round(prior, 3) if research else None,
        "transcript": layer(t_factor, confirms or contradicts),
        "telemetry": layer(m_factor, result in ("confirm", "contradict")),
        "variants": layer(v_factor, used),
        "consensus": round(posterior, 3),
    }
    variant_confirms = sum(1 for v in evidence.get("variants") or [] if v["result"] == "confirm")
    supporting = confirms + (result == "confirm") + variant_confirms

    if result == "contradict" and not single:
        status, reason = "rejected", "telemetry contradicts the claim"
    elif posterior >= config["promote"]["min_confidence"] and supporting >= config["promote"]["min_evidence"]:
        status, reason = "validated", "evidence supports the claim"
    elif posterior <= config["reject"]["max_confidence"] and (contradicts or result == "contradict"
                                                               or any(v["result"] == "contradict"
                                                                      for v in evidence.get("variants") or [])):
        status, reason = "rejected", "evidence contradicts the claim"
    elif not supporting and not contradicts and result is None and not evidence.get("variants"):
        status, reason = "pending", "no transcript, telemetry or variant evidence yet"
    else:
        status, reason = "pending", "evidence not yet strong enough"
    return {"confidence": confidence, "status": status, "reason": reason,
            "counts": {"research_sources": len({r["source"] for r in research}),
                       "transcript_confirmations": len(transcript["confirm"]),
                       "transcript_contradictions": len(transcript["contradict"]),
                       "telemetry": result, "telemetry_laps": laps,
                       "variant_confirmations": variant_confirms}}


def explain(claim_statement, label, scored):
    c, n = scored["confidence"], scored["counts"]
    parts = []
    if c["research"] is not None:
        parts.append(f"research {c['research']:.2f} from {n['research_sources']} source(s)")
    if n["transcript_confirmations"] or n["transcript_contradictions"]:
        parts.append(f"{n['transcript_confirmations']} video(s) confirm, {n['transcript_contradictions']} contradict")
    if n["telemetry"]:
        parts.append(f"telemetry {n['telemetry']}s over {n['telemetry_laps']} lap(s)")
    if n["variant_confirmations"]:
        parts.append(f"confirmed at {n['variant_confirmations']} identical corner(s) of other layouts")
    parts.append(f"consensus {c['consensus']:.2f} -> {scored['status']} ({scored['reason']})")
    return f"{claim_statement} at {label}: " + "; ".join(parts)
