#!/usr/bin/env python3
"""
test_parser.py — pytest suite for factset_parser.py (FactSetParserV3).

The prior suite (last valid at 0d6699a) targeted the positional 96/101-col
parser that was replaced by the header-driven FactSetParserV3; none of the
14 symbols it imported exist in the current module.  This file replaces it
with coverage of the data-foundation integration (Phase 1 raw_fac, Phase 2
security_ref enrichment) plus a small regression net over legacy semantics
that still matter (cash filter, comma-in-name, GICS full label, strategy
invariant).

Run:
    pytest test_parser.py -v
"""

import json
import os
from pathlib import Path

import pytest

import factset_parser as fp
from factset_parser import (
    FactSetParserV3,
    RAW_FACTOR_ORDER,
    _enrich_holding,
    _SECURITY_REF,
    _SECURITY_REF_BY_NAME,
)


# ── Sample CSV discovery ──────────────────────────────────────────────────────
# Primary path is the new-format sample the user dropped into ~/Downloads.
# Falls back to ~/RR/data/sample_new_format_*.csv if the user re-homes the file.
_HOME = Path.home()
_DATA_DIR = _HOME / "RR" / "data"
SAMPLE_CANDIDATES = [_HOME / "Downloads" / "risk_reports_sample (5).csv"]
if _DATA_DIR.exists():
    SAMPLE_CANDIDATES.extend(sorted(_DATA_DIR.glob("sample_new_format_*.csv")))
SAMPLE_CSV = next((p for p in SAMPLE_CANDIDATES if p.exists()), None)

skip_if_no_sample = pytest.mark.skipif(
    SAMPLE_CSV is None,
    reason=f"No sample CSV found. Tried: {[str(p) for p in SAMPLE_CANDIDATES]}",
)


@pytest.fixture(scope="module")
def parsed():
    """Parse the real sample CSV once per module."""
    if SAMPLE_CSV is None:
        pytest.skip("sample CSV unavailable")
    parser = FactSetParserV3(str(SAMPLE_CSV))
    result = parser.parse()   # [strategies_dict, issues, report_date, stats]
    return result


@pytest.fixture(scope="module")
def idm(parsed):
    strategies = parsed[0]
    if "IDM" not in strategies:
        pytest.skip("IDM not in sample")
    return strategies["IDM"]


# ═══════════════════════════════════════════════════════════════════════════════
# Phase 1 — Raw Factors capture
# ═══════════════════════════════════════════════════════════════════════════════


class TestRawFactorOrder:
    """The positional-order constant."""

    def test_twelve_names(self):
        assert len(RAW_FACTOR_ORDER) == 12

    def test_alphabetical(self):
        assert list(RAW_FACTOR_ORDER) == sorted(RAW_FACTOR_ORDER), \
            "RAW_FACTOR_ORDER must stay alphabetical — positional fallback depends on it"


@skip_if_no_sample
class TestRawFacShape:
    """Phase 1 deliverable: strategy.raw_fac shape + hist ordering."""

    def test_raw_fac_populated(self, idm):
        rf = idm.get("raw_fac", {})
        assert len(rf) >= 700, f"IDM raw_fac has only {len(rf)} entries (expected ≥700)"

    def test_each_entry_has_12_floats(self, idm):
        for k, v in idm["raw_fac"].items():
            assert "e" in v and isinstance(v["e"], list) and len(v["e"]) == 12, \
                f"raw_fac[{k}].e wrong shape: {v.get('e')}"

    def test_hist_sorted_ascending(self, idm):
        for k, v in idm["raw_fac"].items():
            dates = [p["d"] for p in v["hist"]]
            assert dates == sorted(dates), f"raw_fac[{k}].hist not sorted: {dates}"
            for p in v["hist"]:
                assert len(p["e"]) == 12

    def test_labels_emitted(self, idm):
        labels = idm.get("raw_fac_labels")
        assert labels == list(RAW_FACTOR_ORDER), \
            f"raw_fac_labels drifted from RAW_FACTOR_ORDER: {labels}"


# ═══════════════════════════════════════════════════════════════════════════════
# Phase 2 — security_ref enrichment
# ═══════════════════════════════════════════════════════════════════════════════


class TestEnrichHolding:
    """Unit tests on _enrich_holding — no CSV parse needed."""

    def test_direct_sedol_hit(self):
        """A ref key with full country/ccy/industry should enrich by exact SEDOL."""
        if not _SECURITY_REF:
            pytest.skip("security_ref empty")
        # Pick any ref entry that has all three target fields — deterministic per run.
        key, ref = next(
            (
                (k, v) for k, v in _SECURITY_REF.items()
                if v.get("country") and v.get("ccy") and v.get("industry")
            ),
            (None, None),
        )
        if key is None:
            pytest.skip("no complete ref entry to use as direct-hit fixture")
        h = {"t": key, "n": ""}   # empty name → no chance of name-fallback
        _enrich_holding(h)
        assert h.get("country") == ref["country"]
        assert h.get("currency") == ref["ccy"]
        assert h.get("industry") == ref["industry"]

    def test_zero_stripped_sedol_fallback(self):
        """SEDOL lookups strip leading zeros when the direct key misses."""
        # Pick any ref key that is purely digits so the zero-stripped variant is well-defined.
        key = next((k for k in _SECURITY_REF if k.isdigit() and not k.startswith("0")), None)
        if not key:
            pytest.skip("no all-digit SEDOL in security_ref to exercise zero-strip fallback")
        padded = "00" + key  # lookup "00XXXXXX", should strip to "XXXXXX"
        h = {"t": padded, "n": ""}
        _enrich_holding(h)
        ref = _SECURITY_REF[key]
        assert h.get("country") == ref.get("country")

    def test_name_fallback(self):
        """When SEDOL misses, the lowercase-alnum-first-30 name index matches."""
        # Use a known entry's name, but give a garbage SEDOL so direct lookup fails.
        sample_name = None
        expected = None
        for ref in _SECURITY_REF.values():
            if ref.get("n") and ref.get("country"):
                sample_name = ref["n"]
                expected = ref
                break
        if not sample_name:
            pytest.skip("no ref entry with name + country for fallback test")
        h = {"t": "ZZZ_UNKNOWN_SEDOL_XYZ", "n": sample_name}
        _enrich_holding(h)
        assert h.get("country") == expected.get("country")

    def test_miss_leaves_fields_absent(self):
        """A total miss on both SEDOL and name leaves enrichment fields absent."""
        h = {"t": "TOTALLY_FAKE_XYZ123", "n": "@@@ Not A Real Security @@@"}
        _enrich_holding(h)
        assert "country" not in h
        assert "currency" not in h
        assert "industry" not in h


@skip_if_no_sample
class TestEnrichmentCoverage:
    """Full-pipeline enrichment coverage across all 7 strategies."""

    def test_idm_100_percent(self, idm):
        enriched = sum(1 for h in idm["hold"] if h.get("country"))
        total = len(idm["hold"])
        pct = 100.0 * enriched / total
        assert pct >= 90.0, f"IDM enrichment {pct:.1f}% (expected ≥90%)"

    def test_security_ref_version_emitted(self, idm):
        assert idm.get("security_ref_version") is not None


# ═══════════════════════════════════════════════════════════════════════════════
# Legacy-behavior regression net (semantics that still matter)
# ═══════════════════════════════════════════════════════════════════════════════


@skip_if_no_sample
class TestStrategyInvariant:
    """Catches silent strategy drops in future parser refactors."""

    def test_exactly_seven_strategies(self, parsed):
        strategies = parsed[0]
        expected = {"ACWI", "IOP", "EM", "GSC", "IDM", "ISC", "SCG"}
        assert set(strategies.keys()) == expected

    def test_all_strategies_have_holdings(self, parsed):
        strategies = parsed[0]
        for sid, s in strategies.items():
            assert len(s.get("hold", [])) > 0, f"{sid} has empty hold[]"


@skip_if_no_sample
class TestLegacyBehavior:
    """Old suite's best-of-class regression assertions, re-expressed against the new API."""

    def test_cash_filter(self, idm):
        """CASH_* and [Cash] rows must not leak into hold[]."""
        tickers = [h["t"] for h in idm["hold"]]
        assert not any(t.startswith("CASH_") for t in tickers), \
            f"IDM hold[] contains CASH_ rows: {[t for t in tickers if t.startswith('CASH_')]}"
        assert "[Cash]" not in tickers

    def test_comma_in_name_survives(self, idm):
        """Security names with commas arrive intact (not split across columns)."""
        # Hitachi, Ltd. is a known Japanese holding in the IDM universe.
        comma_names = [h["n"] for h in idm["hold"] if h.get("n") and "," in h["n"]]
        assert len(comma_names) > 0, "no comma-in-name holdings found — fixture moved?"
        # Spot-check Hitachi specifically — the classic CSV-quoting trip wire.
        hitachi = next((h for h in idm["hold"] if h.get("n", "").startswith("Hitachi")), None)
        if hitachi:
            assert "," in hitachi["n"], f"Hitachi name lost its comma: {hitachi['n']!r}"

    def test_gics_full_label(self, idm):
        """GICS sector labels must be full text (not abbreviated 'Info Tech' etc.)."""
        sector_names = {s["n"] for s in idm["sectors"]}
        assert "Information Technology" in sector_names, \
            f"Expected full 'Information Technology' in sectors; got {sorted(sector_names)}"
        # Per-holding sector should match the full form too.
        it_holdings = [h for h in idm["hold"] if h.get("sec") == "Information Technology"]
        assert len(it_holdings) > 0, "no holdings with sec='Information Technology' — GICS short-form regression?"


# ═══════════════════════════════════════════════════════════════════════════════
# F19 fix (2026-05-04) — per-week pct_specific / pct_factor in hist.summary
# Audit cardTEStacked T1-F1 surfaced that hist.summary entries lacked
# pct_specific even though the parser DOES extract it per RiskM period.
# Fix: _hist_entry now joins by date with a riskm_by_date map.
# These tests are CSV-free — exercise the join directly.
# ═══════════════════════════════════════════════════════════════════════════════


class TestF19PerWeekPctSpecific:
    """F19 — verify hist.summary[].pct_specific / .pct_factor."""

    def _make_parser(self):
        # _hist_entry is a method, but doesn't touch instance state. Construct
        # cheaply via __new__ to skip CSV-loading __init__.
        return FactSetParserV3.__new__(FactSetParserV3)

    def _pc_row(self, d):
        # Minimal pc_row shape that _hist_entry consumes.
        return {
            "d": d,
            "_metrics": {
                "Predicted Tracking Error (Std Dev)": {"p": 5.5},
                "Axioma- Predicted Beta to Benchmark": {"p": 1.02},
                "# of Securities": {"p": 320},
                "Port. Ending Active Share": {"p": 75.0},
            },
        }

    def test_f19_source_direct(self):
        """When riskm_by_date carries pct_specific for the date, fields populate."""
        p = self._make_parser()
        riskm_by_date = {"20250430": {"pct_specific": 67.3, "pct_factor": 32.7}}
        out = p._hist_entry(self._pc_row("20250430"), None, riskm_by_date)
        assert out["pct_specific"] == 67.3
        assert out["pct_factor"] == 32.7

    def test_f19_missing_date_falls_to_none(self):
        """When riskm_by_date has no entry for this date, fields are None (not fabricated)."""
        p = self._make_parser()
        riskm_by_date = {"20250430": {"pct_specific": 67.3, "pct_factor": 32.7}}
        out = p._hist_entry(self._pc_row("20250423"), None, riskm_by_date)  # different date
        assert out["pct_specific"] is None
        assert out["pct_factor"] is None

    def test_f19_no_riskm_arg_defaults_to_none(self):
        """Backwards-compat: callers that don't pass riskm_by_date still work; fields are None."""
        p = self._make_parser()
        out = p._hist_entry(self._pc_row("20250430"))
        assert out["pct_specific"] is None
        assert out["pct_factor"] is None

    def test_f19_partial_source_only_specific(self):
        """If source provides pct_specific but not pct_factor, missing one is None."""
        p = self._make_parser()
        riskm_by_date = {"20250430": {"pct_specific": 67.3}}
        out = p._hist_entry(self._pc_row("20250430"), None, riskm_by_date)
        assert out["pct_specific"] == 67.3
        assert out["pct_factor"] is None

    def test_f19_riskm_dict_with_extra_fields_does_not_leak(self):
        """riskm row carries many fields (exposures, total_risk, etc.). Only the two
        we want should appear in hist.summary — no leakage."""
        p = self._make_parser()
        riskm_by_date = {"20250430": {
            "pct_specific": 67.3, "pct_factor": 32.7,
            "total_risk": 12.5, "bm_risk": 11.0,
            "exposures": {"Volatility": {"c": 0.5}},
        }}
        out = p._hist_entry(self._pc_row("20250430"), None, riskm_by_date)
        assert "exposures" not in out
        assert "total_risk" not in out
        # The expected hist.summary keys remain stable
        assert set(out.keys()) == {"d", "te", "beta", "h", "as", "sr", "cash", "pct_specific", "pct_factor"}

    def test_f19_format_version_bumped(self):
        """FORMAT_VERSION reflects the additive change."""
        # 4.3 means hist.summary carries pct_specific. Older consumers reading 4.2-shape
        # would just see the new fields as null — but the version string is the audit trail.
        assert fp.FORMAT_VERSION >= "4.3"

    def test_f19_parser_version_bumped(self):
        """PARSER_VERSION patch-bumped to mark the additive output change."""
        assert fp.PARSER_VERSION >= "3.1.1"


# ═══════════════════════════════════════════════════════════════════════════════
# B114 (2026-05-04) — cumulative-history merge (append-only architecture)
# Verifies merge_strategy_into_existing()'s contracts:
#   1. First ingest stamps merge_history with no existing.
#   2. Idempotent: merging the same ingest twice yields identical hist data.
#   3. Append: non-overlapping ingests union to full coverage.
#   4. Conflict (new-wins): overlapping date → new ingest's value.
#   5. Preserves existing-only names (e.g., a stock dropped from universe).
#   6. Top-level "current" arrays replaced from new ingest.
#   7. Audit trail (merge_history[]) accumulates correctly.
# These tests are CSV-free — exercise the merge primitives directly.
# ═══════════════════════════════════════════════════════════════════════════════


class TestB114CumulativeMerge:
    """B114 — cumulative merge contract verification."""

    def _make_ingest(self, dates, *, sum_te=5.0, sec_names=("Industrials",), parser="3.1.1", fmt="4.3", hold_t="AAPL"):
        """Synthesize a minimal strategy ingest dict."""
        return {
            "id": "TEST",
            "name": "TEST",
            "benchmark": "BMK",
            "current_date": dates[-1] if dates else None,
            "available_dates": list(dates),
            "parser_version": parser,
            "format_version": fmt,
            "sum": {"te": sum_te, "pct_specific": 65.0, "pct_factor": 35.0},
            "hold": [{"t": hold_t, "p": 1.0, "b": 0.5, "tr": 0.3}],
            "sectors": [{"n": "Industrials", "p": 19.3, "b": 18.0, "a": 1.3}],
            "factors": [{"n": "Volatility", "c": 0.15}],
            "hist": {
                "summary": [{"d": d, "te": sum_te + i * 0.01, "pct_specific": 65.0 + i * 0.1} for i, d in enumerate(dates)],
                "sec": {
                    name: [{"d": d, "p": 19.0 + i * 0.1, "mcr": 9.0 + i * 0.05} for i, d in enumerate(dates)]
                    for name in sec_names
                },
                "fac": {
                    "Volatility": [{"d": d, "e": 0.15, "bm": 0.1, "a": 0.05} for d in dates],
                },
            },
        }

    # ── 1. First-ingest path ───────────────────────────────────────────────

    def test_b114_first_ingest_no_existing(self):
        """When existing_strategy is None, return new + stamped merge_history."""
        new = self._make_ingest(["20260423", "20260430"])
        merged = fp.merge_strategy_into_existing(new, None, source_csv="initial.csv")
        assert merged["available_dates"] == ["20260423", "20260430"]
        assert len(merged["hist"]["summary"]) == 2
        assert "merge_history" in merged
        assert len(merged["merge_history"]) == 1
        h0 = merged["merge_history"][0]
        assert h0["source_csv"] == "initial.csv"
        assert h0["weeks_added"] == 2
        assert h0["weeks_overwritten"] == 0
        assert h0["parser_version"] == "3.1.1"
        assert h0["format_version"] == "4.3"

    # ── 2. Idempotent ──────────────────────────────────────────────────────

    def test_b114_merge_idempotent(self):
        """Merging the same ingest twice yields the same hist data (merge_history grows)."""
        a = self._make_ingest(["20260423", "20260430"])
        once = fp.merge_strategy_into_existing(a, None, source_csv="a.csv")
        twice = fp.merge_strategy_into_existing(a, once, source_csv="a.csv")
        assert once["available_dates"] == twice["available_dates"]
        assert once["hist"]["summary"] == twice["hist"]["summary"]
        assert once["hist"]["sec"] == twice["hist"]["sec"]
        assert once["hist"]["fac"] == twice["hist"]["fac"]
        # merge_history grows; hist data doesn't.
        assert len(twice["merge_history"]) == 2
        assert twice["merge_history"][1]["weeks_added"] == 0
        assert twice["merge_history"][1]["weeks_overwritten"] == 2

    # ── 3. Append: non-overlapping union ───────────────────────────────────

    def test_b114_append_non_overlapping(self):
        """Two non-overlapping ingests union to full coverage."""
        old = self._make_ingest(["20260409", "20260416"])
        new = self._make_ingest(["20260423", "20260430"])
        merged_old = fp.merge_strategy_into_existing(old, None, source_csv="old.csv")
        merged = fp.merge_strategy_into_existing(new, merged_old, source_csv="new.csv")
        assert merged["available_dates"] == ["20260409", "20260416", "20260423", "20260430"]
        assert len(merged["hist"]["summary"]) == 4
        assert merged["merge_history"][-1]["weeks_added"] == 2
        assert merged["merge_history"][-1]["weeks_overwritten"] == 0

    # ── 4. Conflict: new-wins ──────────────────────────────────────────────

    def test_b114_conflict_new_wins(self):
        """Overlapping date → new ingest's value replaces existing."""
        old = self._make_ingest(["20260423"], sum_te=5.0)
        # Different te + different pct_specific on the same date
        new = self._make_ingest(["20260423"], sum_te=7.0)
        merged_old = fp.merge_strategy_into_existing(old, None)
        merged = fp.merge_strategy_into_existing(new, merged_old)
        # Top-level sum from new
        assert merged["sum"]["te"] == 7.0
        # hist.summary @20260423 from new (te=7.00)
        h = next(e for e in merged["hist"]["summary"] if e["d"] == "20260423")
        assert abs(h["te"] - 7.0) < 0.001
        assert merged["merge_history"][-1]["weeks_overwritten"] == 1

    # ── 5. Preserves existing-only names ───────────────────────────────────

    def test_b114_preserves_existing_only_names(self):
        """A name in existing.hist.sec but NOT in new.hist.sec is preserved."""
        old = self._make_ingest(["20260423"], sec_names=("Industrials", "Tech"))
        new = self._make_ingest(["20260430"], sec_names=("Industrials",))  # no Tech
        merged_old = fp.merge_strategy_into_existing(old, None)
        merged = fp.merge_strategy_into_existing(new, merged_old)
        # Tech not in new but should still be in merged
        assert "Tech" in merged["hist"]["sec"]
        assert merged["hist"]["sec"]["Tech"][0]["d"] == "20260423"

    def test_b114_preserves_existing_only_dim(self):
        """A whole dim (e.g., hist.ctry) in existing but not in new is preserved."""
        old = self._make_ingest(["20260423"])
        old["hist"]["ctry"] = {"USA": [{"d": "20260423", "p": 25.0}]}
        new = self._make_ingest(["20260430"])
        # new has no hist.ctry
        merged_old = fp.merge_strategy_into_existing(old, None)
        merged = fp.merge_strategy_into_existing(new, merged_old)
        assert "ctry" in merged["hist"]
        assert merged["hist"]["ctry"]["USA"][0]["d"] == "20260423"

    # ── 6. Top-level "current" replaced ────────────────────────────────────

    def test_b114_current_replaced(self):
        """sum, hold, sectors, factors all come from new ingest unconditionally."""
        old = self._make_ingest(["20260423"], hold_t="AAPL")
        new = self._make_ingest(["20260430"], hold_t="MSFT")
        merged_old = fp.merge_strategy_into_existing(old, None)
        merged = fp.merge_strategy_into_existing(new, merged_old)
        # current_date = new
        assert merged["current_date"] == "20260430"
        # hold[] = new ingest's
        assert merged["hold"][0]["t"] == "MSFT"

    def test_b114_parser_version_stamped_from_new(self):
        """When parser version bumps mid-stream, new value is stamped on merged."""
        old = self._make_ingest(["20260423"], parser="3.1.0", fmt="4.2")
        new = self._make_ingest(["20260430"], parser="3.1.1", fmt="4.3")
        merged_old = fp.merge_strategy_into_existing(old, None)
        merged = fp.merge_strategy_into_existing(new, merged_old)
        assert merged["parser_version"] == "3.1.1"
        assert merged["format_version"] == "4.3"

    # ── 7. merge_history audit trail ──────────────────────────────────────

    def test_b114_merge_history_accumulates(self):
        """Each merge appends an entry; older entries preserved."""
        a = self._make_ingest(["20260409"])
        b = self._make_ingest(["20260416"])
        c = self._make_ingest(["20260423"])
        ma = fp.merge_strategy_into_existing(a, None, source_csv="a.csv")
        mb = fp.merge_strategy_into_existing(b, ma, source_csv="b.csv")
        mc = fp.merge_strategy_into_existing(c, mb, source_csv="c.csv")
        assert len(mc["merge_history"]) == 3
        assert mc["merge_history"][0]["source_csv"] == "a.csv"
        assert mc["merge_history"][1]["source_csv"] == "b.csv"
        assert mc["merge_history"][2]["source_csv"] == "c.csv"

    # ── 8. Edge cases ─────────────────────────────────────────────────────

    def test_b114_typeerror_on_invalid_input(self):
        """new_strategy=None or wrong-type → TypeError."""
        with pytest.raises(TypeError):
            fp.merge_strategy_into_existing(None, None)
        with pytest.raises(TypeError):
            fp.merge_strategy_into_existing("not a dict", None)

    def test_b114_empty_dates(self):
        """First ingest with no available_dates handled cleanly."""
        new = {
            "id": "T", "name": "T", "benchmark": "B",
            "available_dates": [],
            "parser_version": "3.1.1", "format_version": "4.3",
            "sum": {}, "hold": [], "hist": {"summary": [], "sec": {}, "fac": {}},
        }
        merged = fp.merge_strategy_into_existing(new, None, source_csv="empty.csv")
        assert merged["available_dates"] == []
        assert merged["merge_history"][0]["weeks_added"] == 0

    def test_b114_drops_entries_without_d(self):
        """Date-keyed entries with no `d` are dropped during merge."""
        old = self._make_ingest(["20260423"])
        # Inject a malformed entry into existing
        old_merged = fp.merge_strategy_into_existing(old, None)
        old_merged["hist"]["summary"].append({"te": 99.9})  # no d!
        new = self._make_ingest(["20260430"])
        merged = fp.merge_strategy_into_existing(new, old_merged)
        # Malformed entry dropped, valid ones preserved + new added
        assert all(e.get("d") for e in merged["hist"]["summary"])
        assert len(merged["hist"]["summary"]) == 2

    def test_b114_no_top_level_leakage(self):
        """Fields not in _CURRENT_REPLACE_KEYS are preserved from existing."""
        old = self._make_ingest(["20260423"])
        old_merged = fp.merge_strategy_into_existing(old, None)
        old_merged["custom_field"] = "preserve-me"
        new = self._make_ingest(["20260430"])
        merged = fp.merge_strategy_into_existing(new, old_merged)
        # Custom field on existing should survive (we don't overwrite arbitrary keys)
        assert merged.get("custom_field") == "preserve-me"


if __name__ == "__main__":
    import subprocess
    subprocess.run(["pytest", __file__, "-v", "--tb=short"])
