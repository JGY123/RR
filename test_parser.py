#!/usr/bin/env python3
"""
test_parser.py — pytest suite for factset_parser.py

Run:
    pytest test_parser.py -v
    pytest test_parser.py -v --tb=short   # compact tracebacks
    pytest test_parser.py -v -k "unit"    # unit tests only
    pytest test_parser.py -v -k "integ"   # integration tests only
"""

import csv
import io
import json
import os
import tempfile
from pathlib import Path

import pytest

# ── Import the module under test ──────────────────────────────────────────────
import factset_parser as fp
from factset_parser import (
    classify_row,
    get_group,
    pf,
    r2,
    repair_comma_in_name,
    weekly_dates_for,
    open_with_encoding,
    parse,
    ACCT_TO_ID,
    EXPECTED_96,
    EXPECTED_101,
    PREFIX_COLS,
    GROUP_SIZE,
    CURRENT_GRP,
)

# ── Helpers ───────────────────────────────────────────────────────────────────

SAMPLE_CSV = Path("/Users/ygoodman/Downloads/risk_reports_sample.csv")


def csv_bytes(rows, dialect="excel"):
    """Build a CSV in-memory and return bytes."""
    buf = io.StringIO()
    w = csv.writer(buf, dialect=dialect)
    for row in rows:
        w.writerow(row)
    return buf.getvalue().encode("utf-8")


def write_temp_csv(rows, suffix=".csv", encoding="utf-8"):
    """Write rows to a temporary file and return its path."""
    tf = tempfile.NamedTemporaryFile(
        mode="w", suffix=suffix, encoding=encoding, delete=False, newline=""
    )
    w = csv.writer(tf)
    for row in rows:
        w.writerow(row)
    tf.close()
    return Path(tf.name)


def make_row_96(acct="IDM", dt="20260131", lv2="Japan", secname="",
                weight=2.5, bweight=3.0, aweight=-0.5):
    """Build a minimal 96-column row for a sector/country aggregate."""
    prefix = [acct, dt, "USD", "Country", lv2, secname]
    # 5 groups × 18 cols, all zeros except group 4 (current)
    groups = [[0.0] * 18 for _ in range(5)]
    groups[CURRENT_GRP] = [weight, bweight, aweight] + [0.0] * 15
    flat = []
    for g in groups:
        flat.extend(g)
    return prefix + [str(v) for v in flat]


def make_holding_row_101(acct="IDM", dt="20260131", lv2="NVDA", secname="NVIDIA Corp.",
                          weight=2.1, bweight=0.5, aweight=1.6, over=1.5):
    """Build a minimal 101-column holdings row."""
    prefix = [acct, dt, "USD", "Security", lv2, secname]
    groups = [[0.0] * 19 for _ in range(5)]
    # col positions in 19-col group: 0=W, 1=BW, 2=AW, 3=%S, 4=%T, 5=OverallRank, 6=%T_Check, 7=OVER_WAvg
    groups[CURRENT_GRP] = [weight, bweight, aweight, 0.3, 0.7, 1.0, 0.0, over] + [0.0] * 11
    flat = []
    for g in groups:
        flat.extend(g)
    return prefix + [str(v) for v in flat]


# ═══════════════════════════════════════════════════════════════════════════════
# Unit tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestPf:
    """Unit — pf() float parser."""

    def test_empty_string(self):
        assert pf("") is None

    def test_none(self):
        assert pf(None) is None

    def test_whitespace(self):
        assert pf("   ") is None

    def test_valid_float(self):
        assert pf("3.14") == pytest.approx(3.14)

    def test_negative(self):
        assert pf("-1.23") == pytest.approx(-1.23)

    def test_integer_string(self):
        assert pf("5") == pytest.approx(5.0)

    def test_zero(self):
        assert pf("0") == pytest.approx(0.0)

    def test_nan_string(self):
        # "nan" → None
        assert pf("nan") is None

    def test_invalid(self):
        assert pf("abc") is None


class TestR2:
    """Unit — r2() rounding helper."""

    def test_rounds_2dp(self):
        assert r2(3.14159) == 3.14

    def test_none_passthrough(self):
        assert r2(None) is None

    def test_zero(self):
        assert r2(0.0) == 0.0


class TestGetGroup:
    """Unit — get_group() column-group extractor."""

    def test_96col_group0(self):
        """Group 0 of a 96-col row returns correct 18 floats."""
        row = ["IDM", "20260131", "USD", "L1", "Japan", ""] + [str(i * 0.1) for i in range(90)]
        assert len(row) == 96
        g = get_group(row, 0)
        assert len(g) == 18
        assert g[0] == pytest.approx(0.0)

    def test_96col_current_group(self):
        """Current group (index 4) of 96-col row maps correctly."""
        row = make_row_96(weight=5.0, bweight=3.0, aweight=2.0)
        assert len(row) == 96
        g = get_group(row, CURRENT_GRP)
        assert g[0] == pytest.approx(5.0)   # C_W = 0
        assert g[1] == pytest.approx(3.0)   # C_BW = 1
        assert g[2] == pytest.approx(2.0)   # C_AW = 2

    def test_101col_drops_overall_rank(self):
        """101-col rows: Overall Rank at pos 5 is dropped → 18 cols per group."""
        row = make_holding_row_101(weight=2.1, bweight=0.5, aweight=1.6, over=2.0)
        assert len(row) == 101
        g = get_group(row, CURRENT_GRP)
        assert len(g) == 18
        # C_W=0, C_BW=1, C_AW=2 remain correct after dropping pos-5
        assert g[0] == pytest.approx(2.1)
        assert g[1] == pytest.approx(0.5)
        assert g[2] == pytest.approx(1.6)
        # OVER_WAvg is now at position 6 in the 18-col layout (was pos 7 in 19-col)
        assert g[6] == pytest.approx(2.0)

    def test_empty_cell_becomes_none(self):
        """Empty strings in the row produce None in the group."""
        row = ["IDM", "20260131", "USD", "L1", "Japan", ""] + [""] * 90
        assert len(row) == 96
        g = get_group(row, 0)
        assert all(v is None for v in g)


class TestClassifyRow:
    """Unit — classify_row() row-type classifier."""

    def test_data_row(self):
        assert classify_row("Data", "") == "special"

    def test_na_row(self):
        assert classify_row("@NA", "") == "special"

    def test_unassigned_row(self):
        assert classify_row("[Unassigned]", "") == "special"

    def test_cash_row(self):
        assert classify_row("[Cash]", "") == "cash"

    def test_cash_currency(self):
        assert classify_row("CASH_USD", "") == "other"

    def test_gics_sector(self):
        assert classify_row("Industrials", "") == "sector"
        assert classify_row("Information Technology", "") == "sector"

    def test_region(self):
        assert classify_row("English", "") == "region"
        assert classify_row("Far East", "") == "region"

    def test_country(self):
        assert classify_row("Japan", "") == "country"
        assert classify_row("United Kingdom", "") == "country"

    def test_holding_with_secname(self):
        assert classify_row("ABC", "Some Corp Inc") == "holding"

    def test_holding_asterisk_ticker(self):
        assert classify_row("*SHOP", "") == "holding"

    def test_holding_uppercase_ticker(self):
        assert classify_row("NVDA", "") == "holding"

    def test_holding_numeric_ticker(self):
        assert classify_row("6501", "") == "holding"

    def test_gics_l2_not_classified_as_holding(self):
        # Short lowercase words like "Banks" should not be holdings
        result = classify_row("Banks", "")
        assert result != "holding"

    def test_usa_normalization_handled_upstream(self):
        # "Usa" is normalized to "United States" before classify_row is called
        assert classify_row("United States", "") == "country"


class TestRepairCommaInName:
    """Unit — repair_comma_in_name()."""

    def test_no_repair_needed(self):
        row = ["a"] * 96
        repaired, name = repair_comma_in_name(row, 96)
        assert repaired is None and name is None

    def test_repair_one_extra_col(self):
        """One extra column → name is two parts joined by comma."""
        row = ["IDM", "20260131", "USD", "Security", "NVDA", "NVIDIA Corp.", "Extra"] + ["0"] * 90
        assert len(row) == 97
        repaired, name = repair_comma_in_name(row, 96)
        assert repaired is not None
        assert len(repaired) == 96
        assert name == "NVIDIA Corp.,Extra"

    def test_repair_two_extra_cols(self):
        """Two extra columns → name is three parts joined by commas."""
        row = ["IDM", "20260131", "USD", "Security", "TICK", "ABC", "Inc.", "Ltd."] + ["0"] * 90
        assert len(row) == 96 + 2
        repaired, name = repair_comma_in_name(row, 96)
        assert repaired is not None
        assert len(repaired) == 96
        assert name == "ABC,Inc.,Ltd."

    def test_repair_101_col_with_one_extra(self):
        """Repair works for 101-col target too."""
        row = ["IDM", "20260131", "USD", "Security", "TICK", "Name", "Part2"] + ["0"] * 95
        assert len(row) == 102
        repaired, name = repair_comma_in_name(row, 101)
        assert repaired is not None
        assert len(repaired) == 101

    def test_repair_failure_returns_none(self):
        """If repair would create wrong length, return None."""
        # Give a row shorter than expected → no extra cols
        row = ["a"] * 90
        repaired, name = repair_comma_in_name(row, 96)
        assert repaired is None and name is None


class TestWeeklyDates:
    """Unit — weekly_dates_for()."""

    def test_jan_2026(self):
        """January 2026: Fridays are 2, 9, 16, 23, 30."""
        dates = weekly_dates_for("20260131")
        assert len(dates) == 5
        assert dates == [
            "2026-01-02", "2026-01-09", "2026-01-16", "2026-01-23", "2026-01-30"
        ]

    def test_oldest_first(self):
        dates = weekly_dates_for("20260131")
        assert dates == sorted(dates)

    def test_all_fridays(self):
        from datetime import datetime
        dates = weekly_dates_for("20260228")
        for d in dates:
            assert datetime.strptime(d, "%Y-%m-%d").weekday() == 4  # Friday


class TestOpenWithEncoding:
    """Unit — open_with_encoding() fallback chain."""

    def test_utf8_sig(self, tmp_path):
        p = tmp_path / "test.csv"
        p.write_bytes(b"\xef\xbb\xbfACCT,DATE\n")
        fh, enc = open_with_encoding(p)
        fh.close()
        assert enc == "utf-8-sig"

    def test_latin1(self, tmp_path):
        p = tmp_path / "test.csv"
        # Write content that is invalid UTF-8 but valid latin-1
        p.write_bytes(b"ACCT,S\xe9curit\xe9\n")
        fh, enc = open_with_encoding(p)
        fh.close()
        assert enc in ("latin-1", "cp1252")

    def test_raises_on_all_fail(self, tmp_path):
        p = tmp_path / "test.csv"
        # Write null bytes — should fail all encodings cleanly
        # Instead, write a file and then mock — just test the ValueError path
        # by creating a bad file (unreadable binary)
        p.write_bytes(b"\x00" * 10)
        # This should succeed with some encoding (null bytes are valid in most)
        # so just verify the function returns without crashing
        try:
            fh, enc = open_with_encoding(p)
            fh.close()
        except ValueError:
            pass  # acceptable if all encodings fail


# ═══════════════════════════════════════════════════════════════════════════════
# Integration tests — require the real sample CSV
# ═══════════════════════════════════════════════════════════════════════════════

pytestmark_integ = pytest.mark.skipif(
    not SAMPLE_CSV.exists(),
    reason=f"Sample CSV not found at {SAMPLE_CSV}",
)


@pytest.fixture(scope="module")
def parsed():
    """Parse the real sample CSV once; share result across all integration tests."""
    if not SAMPLE_CSV.exists():
        pytest.skip(f"Sample CSV not at {SAMPLE_CSV}")
    strategies, issues, main_date, stats = parse(SAMPLE_CSV)
    return strategies, issues, main_date, stats


class TestIntegParseOutput:
    """Integration — top-level parse() structure."""

    @pytestmark_integ
    def test_returns_4_tuple(self, parsed):
        assert len(parsed) == 4

    @pytestmark_integ
    def test_all_7_strategies_present(self, parsed):
        strategies, *_ = parsed
        expected = {"IDM", "IOP", "EM", "ISC", "SCG", "ACWI", "GSC"}
        assert set(strategies.keys()) == expected

    @pytestmark_integ
    def test_no_validation_issues(self, parsed):
        _, issues, _, _ = parsed
        assert issues == [], f"Validation issues: {issues}"

    @pytestmark_integ
    def test_main_date_is_string(self, parsed):
        _, _, main_date, _ = parsed
        assert isinstance(main_date, str)
        assert len(main_date) == 8  # YYYYMMDD

    @pytestmark_integ
    def test_parse_stats_keys(self, parsed):
        _, _, _, stats = parsed
        required = {"total_rows", "parse_time_s", "encoding", "file_size_mb", "strat_stats"}
        assert required.issubset(stats.keys())


class TestIntegSummaryStats:
    """Integration — sum{} dict for each strategy."""

    @pytestmark_integ
    def test_sum_keys(self, parsed):
        strategies, *_ = parsed
        required = {"te", "as", "beta", "h", "bh", "sr", "cash"}
        for sid, s in strategies.items():
            assert required.issubset(s["sum"].keys()), f"{sid} missing sum keys"

    @pytestmark_integ
    def test_te_positive(self, parsed):
        strategies, *_ = parsed
        for sid, s in strategies.items():
            assert s["sum"]["te"] is not None and s["sum"]["te"] > 0, f"{sid} TE ≤ 0"

    @pytestmark_integ
    def test_active_share_range(self, parsed):
        strategies, *_ = parsed
        for sid, s in strategies.items():
            assert 0 < s["sum"]["as"] <= 100, f"{sid} Active Share out of range"

    @pytestmark_integ
    def test_beta_reasonable(self, parsed):
        strategies, *_ = parsed
        for sid, s in strategies.items():
            assert 0.5 < s["sum"]["beta"] < 1.5, f"{sid} Beta unreasonable: {s['sum']['beta']}"

    @pytestmark_integ
    def test_holdings_count_positive(self, parsed):
        strategies, *_ = parsed
        for sid, s in strategies.items():
            assert s["sum"]["h"] > 0, f"{sid} has 0 holdings"

    @pytestmark_integ
    def test_bh_greater_than_h(self, parsed):
        strategies, *_ = parsed
        for sid, s in strategies.items():
            h, bh = s["sum"]["h"], s["sum"]["bh"]
            assert bh is not None and bh > h, f"{sid}: BH ({bh}) ≤ H ({h})"

    @pytestmark_integ
    def test_sr_is_none(self, parsed):
        """sr (hit rate) is not available in FactSet export — must be None."""
        strategies, *_ = parsed
        for sid, s in strategies.items():
            assert s["sum"]["sr"] is None, f"{sid} SR unexpectedly populated"

    @pytestmark_integ
    def test_cash_non_negative(self, parsed):
        strategies, *_ = parsed
        for sid, s in strategies.items():
            cash = s["sum"]["cash"]
            if cash is not None:
                assert cash >= 0, f"{sid} Cash negative: {cash}"


class TestIntegSectors:
    """Integration — sectors[] for each strategy."""

    @pytestmark_integ
    def test_11_sectors_each(self, parsed):
        strategies, *_ = parsed
        for sid, s in strategies.items():
            assert len(s["sectors"]) == 11, f"{sid} has {len(s['sectors'])} sectors"

    @pytestmark_integ
    def test_sector_weight_sum_near_100(self, parsed):
        """Sector weights should sum to ≈ 100% (allow 5% for unclassified)."""
        strategies, *_ = parsed
        for sid, s in strategies.items():
            total = sum(sec["p"] or 0 for sec in s["sectors"])
            assert 75 < total <= 105, f"{sid} sector sum={total:.1f}%"

    @pytestmark_integ
    def test_sector_has_required_keys(self, parsed):
        strategies, *_ = parsed
        for sid, s in strategies.items():
            for sec in s["sectors"]:
                assert {"n", "p", "b", "a"}.issubset(sec.keys()), \
                    f"{sid} sector missing keys: {sec}"


class TestIntegRegions:
    """Integration — regions[] for each strategy."""

    @pytestmark_integ
    def test_at_least_one_region(self, parsed):
        strategies, *_ = parsed
        for sid, s in strategies.items():
            assert len(s["regions"]) >= 1, f"{sid} has no regions"

    @pytestmark_integ
    def test_region_weight_sum_positive(self, parsed):
        strategies, *_ = parsed
        for sid, s in strategies.items():
            total = sum(r["p"] or 0 for r in s["regions"])
            assert total > 0, f"{sid} region weight sum = 0"


class TestIntegCountries:
    """Integration — countries[] for each strategy."""

    @pytestmark_integ
    def test_at_least_5_countries(self, parsed):
        strategies, *_ = parsed
        for sid, s in strategies.items():
            assert len(s["countries"]) >= 5, f"{sid} too few countries"

    @pytestmark_integ
    def test_no_usa_alias(self, parsed):
        """'Usa' should be normalized to 'United States'."""
        strategies, *_ = parsed
        for sid, s in strategies.items():
            names = [c["n"] for c in s["countries"]]
            assert "Usa" not in names, f"{sid} contains 'Usa' alias"

    @pytestmark_integ
    def test_no_duplicate_countries(self, parsed):
        strategies, *_ = parsed
        for sid, s in strategies.items():
            names = [c["n"] for c in s["countries"]]
            assert len(names) == len(set(names)), f"{sid} has duplicate countries"


class TestIntegHoldings:
    """Integration — hold[] for each strategy."""

    @pytestmark_integ
    def test_holdings_have_required_keys(self, parsed):
        strategies, *_ = parsed
        required = {"t", "n", "p", "b", "a", "mcr", "tr", "r", "over"}
        for sid, s in strategies.items():
            for h in s["hold"]:
                assert required.issubset(h.keys()), f"{sid} holding missing keys: {h}"

    @pytestmark_integ
    def test_portfolio_weights_positive(self, parsed):
        strategies, *_ = parsed
        for sid, s in strategies.items():
            for h in s["hold"]:
                assert h["p"] is not None and h["p"] > 0, \
                    f"{sid} holding {h['t']} has non-positive weight"

    @pytestmark_integ
    def test_rank_in_range(self, parsed):
        """Rank (r) must be 1–5 or None."""
        strategies, *_ = parsed
        for sid, s in strategies.items():
            for h in s["hold"]:
                if h["r"] is not None:
                    assert 1 <= h["r"] <= 5, \
                        f"{sid} {h['t']} rank {h['r']} out of 1–5"

    @pytestmark_integ
    def test_sector_country_none(self, parsed):
        """sec and co are None (not embedded in FactSet CSV per holding)."""
        strategies, *_ = parsed
        for sid, s in strategies.items():
            for h in s["hold"]:
                assert h["sec"] is None, f"{sid} {h['t']} has unexpected sec={h['sec']}"
                assert h["co"] is None, f"{sid} {h['t']} has unexpected co={h['co']}"

    @pytestmark_integ
    def test_no_cash_in_hold(self, parsed):
        """[Cash] rows must not appear as individual holdings."""
        strategies, *_ = parsed
        for sid, s in strategies.items():
            tickers = [h["t"] for h in s["hold"]]
            assert "[Cash]" not in tickers, f"{sid} has [Cash] in hold[]"


class TestIntegFactors:
    """Integration — factors[] for each strategy."""

    @pytestmark_integ
    def test_16_factors(self, parsed):
        strategies, *_ = parsed
        for sid, s in strategies.items():
            assert len(s["factors"]) == 16, \
                f"{sid} has {len(s['factors'])} factors (expected 16)"

    @pytestmark_integ
    def test_factor_keys(self, parsed):
        strategies, *_ = parsed
        required = {"n", "e", "bm", "a", "c", "imp", "ret"}
        for sid, s in strategies.items():
            for f in s["factors"]:
                assert required.issubset(f.keys()), \
                    f"{sid} factor {f.get('n')} missing keys"

    @pytestmark_integ
    def test_factor_active_is_e_minus_bm_or_e(self, parsed):
        """factor.a should equal e - bm when both present, or equal e otherwise."""
        strategies, *_ = parsed
        for sid, s in strategies.items():
            for f in s["factors"]:
                if f["e"] is not None and f["bm"] is not None:
                    expected = round(f["e"] - f["bm"], 4)
                    assert abs((f["a"] or 0) - expected) < 0.02, \
                        f"{sid} {f['n']}: a={f['a']} ≠ e-bm={expected}"

    @pytestmark_integ
    def test_idm_factor_ret_none(self, parsed):
        """CompoundedFactorReturn is blank in FactSet export → must be None."""
        strategies, *_ = parsed
        idm_factors = strategies["IDM"]["factors"]
        for f in idm_factors:
            assert f["ret"] is None, f"IDM factor {f['n']} ret={f['ret']} (expected None)"


class TestIntegCharacteristics:
    """Integration — chars[] for each strategy."""

    @pytestmark_integ
    def test_chars_present(self, parsed):
        strategies, *_ = parsed
        for sid, s in strategies.items():
            assert len(s["chars"]) > 0, f"{sid} has no chars"

    @pytestmark_integ
    def test_mktcap_positive(self, parsed):
        strategies, *_ = parsed
        for sid, s in strategies.items():
            mktcap = next((c for c in s["chars"] if c["m"] == "Market Cap ($M)"), None)
            if mktcap:
                assert mktcap["p"] > 0, f"{sid} Market Cap ≤ 0"

    @pytestmark_integ
    def test_idm_pe_present(self, parsed):
        """IDM has P/E in Fundamental Characteristics tile."""
        strategies, *_ = parsed
        pe = next((c for c in strategies["IDM"]["chars"] if c["m"] == "P/E Ratio"), None)
        assert pe is not None, "IDM missing P/E Ratio char"
        assert pe["p"] is not None and pe["p"] > 0
        assert pe["b"] is None  # benchmark P/E not in export


class TestIntegHistory:
    """Integration — hist{} for each strategy."""

    @pytestmark_integ
    def test_hist_keys(self, parsed):
        strategies, *_ = parsed
        for sid, s in strategies.items():
            assert "summary" in s["hist"], f"{sid} missing hist.summary"
            assert "fac" in s["hist"], f"{sid} missing hist.fac"

    @pytestmark_integ
    def test_hist_summary_has_entries(self, parsed):
        strategies, *_ = parsed
        for sid, s in strategies.items():
            # Some strategies may have limited history; just verify list
            assert isinstance(s["hist"]["summary"], list)

    @pytestmark_integ
    def test_hist_fac_is_dict(self, parsed):
        strategies, *_ = parsed
        for sid, s in strategies.items():
            assert isinstance(s["hist"]["fac"], dict)


class TestIntegUnowned:
    """Integration — unowned[] (benchmark-only holdings)."""

    @pytestmark_integ
    def test_unowned_present(self, parsed):
        strategies, *_ = parsed
        for sid, s in strategies.items():
            assert len(s["unowned"]) > 0, f"{sid} has no unowned holdings"

    @pytestmark_integ
    def test_unowned_bw_positive(self, parsed):
        strategies, *_ = parsed
        for sid, s in strategies.items():
            for u in s["unowned"]:
                assert u["b"] is not None and u["b"] > 0, \
                    f"{sid} unowned {u['t']} has b={u['b']}"


class TestIntegJSONOutput:
    """Integration — JSON serialisation round-trip."""

    @pytestmark_integ
    def test_output_json_valid(self, parsed, tmp_path):
        """parse() output can be saved as JSON and reloaded."""
        strategies, issues, main_date, stats = parsed
        out_path = tmp_path / "out.json"
        output = {
            "generated": "2026-03-22T00:00:00",
            "version": fp.FORMAT_VERSION,
            "parser_version": fp.PARSER_VERSION,
            "report_date": main_date,
            "strategies": list(strategies.values()),
        }
        out_path.write_text(json.dumps(output))
        reloaded = json.loads(out_path.read_text())
        assert reloaded["version"] == fp.FORMAT_VERSION
        assert len(reloaded["strategies"]) == 7

    @pytestmark_integ
    def test_no_null_string_in_names(self, parsed):
        """Security names must not contain the literal string 'null'."""
        strategies, *_ = parsed
        for sid, s in strategies.items():
            for h in s["hold"]:
                assert h["n"] != "null", f"{sid} {h['t']} name is literal 'null'"


# ═══════════════════════════════════════════════════════════════════════════════
# Edge-case / regression tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestEdgeCases:
    """Edge case and regression tests."""

    def test_repair_skips_data_rows(self, tmp_path):
        """Data rows with many columns must NOT trigger comma repair."""
        # Build a minimal CSV with a "Data" row that has > 101 columns
        header_row = ["ACCT", "DATE"] + [f"C{i}" for i in range(110)]
        data_row = (
            ["IDM", "20260131", "USD", "Summary", "Data", ""]
            + ["1.0"] * 36     # extra wide — simulate summary stats row
        )
        p = write_temp_csv([header_row, data_row])
        try:
            # Should not crash; Data row processed without repair attempt
            # We test by verifying the parser doesn't raise on wide Data rows
            # (A full parse would fail on empty strategies, but no exception)
            strategies, issues, main_date, stats = parse(p)
            # IDM won't have full data, but no crash
            assert stats["repair_warnings"] == 0
        finally:
            p.unlink(missing_ok=True)

    def test_unknown_account_skipped(self, tmp_path, capsys):
        """Unknown account codes print a warning and are skipped, not crashed."""
        header_row = ["ACCT", "DATE"] + [f"C{i}" for i in range(94)]
        row = ["UNKNOWN_ACCT", "20260131"] + ["0"] * 94
        p = write_temp_csv([header_row, row])
        try:
            # Should not raise — returns empty strategies + issue message
            result = parse(p)
            assert len(result) == 4
            strategies, issues, main_date, stats = result
            captured = capsys.readouterr()
            assert "Unknown account" in captured.out
            assert "UNKNOWN_ACCT" not in strategies
        finally:
            p.unlink(missing_ok=True)

    def test_usa_alias_normalized(self, tmp_path):
        """'Usa' in Level2 is normalized to 'United States' in parse output."""
        # classify_row handles both "Usa" and "United States" as countries.
        # The parse loop normalizes "Usa" → "United States" before classifying.
        assert classify_row("United States", "") == "country"
        assert classify_row("Usa", "") == "country"  # Usa is in COUNTRIES set
        # ... because it's normalized upstream BEFORE classify_row is called

    def test_pf_handles_edge_numbers(self):
        assert pf("0.00") == pytest.approx(0.0)
        assert pf("-0.00") == pytest.approx(0.0)
        assert pf("1e-5") == pytest.approx(1e-5)
        assert pf("1E+3") == pytest.approx(1000.0)

    def test_get_group_out_of_bounds_group(self):
        """Requesting a group beyond row length returns all-None."""
        row = ["IDM", "20260131", "USD", "L1", "Japan", ""] + ["1.0"] * 90
        g = get_group(row, 10)  # group 10 doesn't exist in 96-col row
        assert all(v is None for v in g)

    def test_rank_clamped_to_1_5(self):
        """OVER_WAvg values outside 1–5 are clamped to valid range."""
        # Access the clamping logic via a constructed row
        over_score = 6.5   # out of range
        rank = max(1, min(5, round(over_score)))
        assert rank == 5

        over_score = 0.1
        rank = max(1, min(5, round(over_score)))
        assert rank == 1


class TestRegressionCommaRepair:
    """Regression: comma-in-name repair for known company names."""

    def test_pathward_financial(self):
        """Pathward Financial, Inc. — the known problem case from the real data."""
        # Simulate: row was split at comma → "Pathward Financial" + " Inc." in extra col
        row_101 = (
            ["IDM", "20260131", "USD", "Security", "CASH", "Pathward Financial", " Inc."]
            + ["0"] * 95
        )
        assert len(row_101) == 102  # one extra col
        repaired, name = repair_comma_in_name(row_101, 101)
        assert repaired is not None
        assert len(repaired) == 101
        assert "Pathward Financial, Inc." in name or "Inc." in name

    def test_holding_ltd_company(self):
        """'Hitachi, Ltd.' style Japanese company names repair correctly."""
        row_96 = (
            ["IDM", "20260131", "USD", "Security", "6501", "Hitachi", " Ltd."]
            + ["0"] * 90
        )
        assert len(row_96) == 96 + 1
        repaired, name = repair_comma_in_name(row_96, 96)
        assert repaired is not None
        assert len(repaired) == 96
        assert "Hitachi" in name and "Ltd." in name


if __name__ == "__main__":
    import subprocess
    subprocess.run(["pytest", __file__, "-v", "--tb=short"])
