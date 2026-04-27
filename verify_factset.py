#!/usr/bin/env python3
"""
verify_factset.py — Run a structured pass/fail audit of the parsed FactSet JSON
against every ask from FACTSET_CALL_PREP / factset_call_deck.html.

Usage:
  python3 verify_factset.py [path/to/latest_data.json] [path/to/source.csv]

If no args, defaults to:
  ~/RR/latest_data.json  (parsed output from load_data.sh)
  newest *.csv in ~/Downloads (the source CSV)

Output:
  - Color-coded console report (✓ pass, ◐ partial, ● fail)
  - Per-strategy summary if multi-strategy file
  - Final verdict: GREEN-LIGHT / FIX-REQUIRED with specific items needing FactSet follow-up
"""

import json
import os
import sys
import glob
from pathlib import Path

# ANSI colors
RESET = "\033[0m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
RED = "\033[31m"
DIM = "\033[2m"
BOLD = "\033[1m"
CYAN = "\033[36m"

PASS = f"{GREEN}✓{RESET}"
PART = f"{YELLOW}◐{RESET}"
FAIL = f"{RED}●{RESET}"
WARN = f"{YELLOW}⚠{RESET}"


# Required factor sets per the call deck
STYLE_FACTORS_12 = {
    "Medium-Term Momentum", "Volatility", "Growth", "Value",
    "Dividend Yield", "Earnings Yield", "Profitability", "Size",
    "Leverage", "Liquidity", "Market Sensitivity", "Exchange Rate Sensitivity",
}
MACRO_FACTORS_4 = {"Market", "Industry", "Country", "Currency"}
ALL_16_FACTORS = STYLE_FACTORS_12 | MACRO_FACTORS_4

# Identifier fields user added during the call
IDENTIFIER_KEYS = {"sedol", "cusip", "isin", "ticker_region", "tkr"}

results = []   # list of (status, name, msg)


def add(status, name, msg=""):
    results.append((status, name, msg))


def header(text, ch="="):
    bar = ch * 78
    print(f"\n{BOLD}{CYAN}{bar}\n{text}\n{bar}{RESET}")


def sub(text):
    print(f"\n{BOLD}{text}{RESET}")


# ============== load ==============

def load_json(path):
    with open(path) as f:
        return json.load(f)


def find_default_csv():
    csvs = sorted(glob.glob(os.path.expanduser("~/Downloads/*.csv")), key=os.path.getmtime, reverse=True)
    return csvs[0] if csvs else None


# ============== checks ==============

def check_strategy(strat_id, strat, csv_text=None):
    """Run all per-strategy checks. Returns list of (status, name, msg)."""
    out = []
    hold = strat.get("hold") or []
    factors = strat.get("factors") or []
    sectors = strat.get("sectors") or []
    countries = strat.get("countries") or []
    regions = strat.get("regions") or []
    chars = strat.get("chars") or []
    summary = strat.get("sum") or {}
    snap_attrib = strat.get("snap_attrib") or {}

    # ---- A1: holdings completeness ----
    port_h = sum(1 for h in hold if (h.get("p") or 0) > 0)
    bench_h = sum(1 for h in hold if (h.get("b") or 0) > 0)
    summary_count = summary.get("h")
    total_rows = len(hold)
    if summary_count and port_h:
        coverage_pct = (port_h / summary_count) * 100 if summary_count else 0
        if total_rows >= summary_count * 0.95:
            out.append((PASS, "A1 Holdings completeness",
                        f"{port_h} port + {bench_h} bench in {total_rows} rows (summary expects {summary_count})"))
        else:
            out.append((FAIL, "A1 Holdings completeness",
                        f"only {total_rows} rows but summary count = {summary_count} ({coverage_pct:.0f}% port coverage)"))
    else:
        out.append((PART, "A1 Holdings completeness",
                    f"{total_rows} holdings (could not compare against summary count)"))

    # ---- A2: per-stock factor data (16 factors) ----
    sample = next((h for h in hold if h.get("factor_contr")), None)
    if sample:
        keys = set(sample.get("factor_contr", {}).keys())
        if len(keys) == 16 and ALL_16_FACTORS.issubset(keys):
            out.append((PASS, "A2 Per-stock factor_contr (16 factors)",
                        f"{len(keys)} factor keys present"))
        elif keys >= STYLE_FACTORS_12:
            missing = ALL_16_FACTORS - keys
            out.append((PART, "A2 Per-stock factor_contr",
                        f"{len(keys)} keys; missing: {', '.join(sorted(missing))}"))
        else:
            missing_styles = STYLE_FACTORS_12 - keys
            out.append((FAIL, "A2 Per-stock factor_contr",
                        f"only {len(keys)} keys; missing styles: {', '.join(sorted(missing_styles))}"))
    else:
        out.append((FAIL, "A2 Per-stock factor_contr",
                    "no holding has factor_contr populated"))

    # ---- NEW from call: per-holding identifiers ----
    if sample:
        id_present = [k for k in IDENTIFIER_KEYS if any(h.get(k) for h in hold[:50])]
        sedol_count = sum(1 for h in hold if h.get("sedol"))
        cusip_count = sum(1 for h in hold if h.get("cusip"))
        isin_count = sum(1 for h in hold if h.get("isin"))
        tkr_region = sum(1 for h in hold if h.get("ticker_region") or h.get("tkr_region"))
        if sedol_count > 0 or cusip_count > 0 or isin_count > 0:
            out.append((PASS, "NEW Identifiers (SEDOL/CUSIP/ISIN/Ticker-Region)",
                        f"SEDOL: {sedol_count}, CUSIP: {cusip_count}, ISIN: {isin_count}, Tkr-Region: {tkr_region}"))
        else:
            out.append((FAIL, "NEW Identifiers (SEDOL/CUSIP/ISIN/Ticker-Region)",
                        "no SEDOL/CUSIP/ISIN field populated on any holding"))

    # ---- NEW: per-holding market cap ----
    mcap_count = sum(1 for h in hold if h.get("mcap") or h.get("market_cap"))
    if mcap_count >= total_rows * 0.5:
        out.append((PASS, "NEW Per-holding market cap",
                    f"{mcap_count}/{total_rows} holdings have market_cap"))
    elif mcap_count > 0:
        out.append((PART, "NEW Per-holding market cap",
                    f"only {mcap_count}/{total_rows} have market_cap"))
    else:
        out.append((FAIL, "NEW Per-holding market cap",
                    "no market_cap field on holdings"))

    # ---- NEW: per-holding raw factor exposures (separate from factor_contr) ----
    raw_exp_keys = []
    if sample:
        raw_exp_keys = [k for k in sample.keys() if k.endswith("_exp") or k.endswith("_loading")]
    raw_exp_count = sum(1 for h in hold if any(h.get(k) is not None for k in raw_exp_keys))
    if len(raw_exp_keys) >= 12:
        out.append((PASS, "NEW Per-holding raw factor exposures (z-scores)",
                    f"{len(raw_exp_keys)} *_exp keys, populated on {raw_exp_count}/{total_rows}"))
    elif len(raw_exp_keys) > 0:
        out.append((PART, "NEW Per-holding raw factor exposures",
                    f"{len(raw_exp_keys)} *_exp keys (expected 12)"))
    else:
        # Fallback check — sometimes shipped under different field name
        if sample and any(k for k in sample.keys() if "loading" in k.lower() or "z_" in k.lower()):
            out.append((PART, "NEW Per-holding raw factor exposures",
                        "alt field naming detected — verify schema"))
        else:
            out.append((FAIL, "NEW Per-holding raw factor exposures",
                        "no raw_exp / z-score columns on holdings"))

    # ---- NEW: per-holding period return ----
    r_count = sum(1 for h in hold if h.get("r") is not None or h.get("ret") is not None or h.get("period_return") is not None)
    if r_count >= total_rows * 0.5:
        out.append((PASS, "NEW Per-holding period return",
                    f"{r_count}/{total_rows} holdings have a period return field"))
    elif r_count > 0:
        out.append((PART, "NEW Per-holding period return",
                    f"only {r_count}/{total_rows} populated"))
    else:
        out.append((FAIL, "NEW Per-holding period return",
                    "no period return field on holdings (Brinson blocked)"))

    # ---- A3 + benchmark absolute exposure (NEW: f.bm populated) ----
    if factors:
        with_a = sum(1 for f in factors if f.get("a") is not None)
        with_e = sum(1 for f in factors if f.get("e") is not None)
        with_bm = sum(1 for f in factors if f.get("bm") is not None)
        with_c = sum(1 for f in factors if f.get("c") is not None)
        synth_c = sum(1 for f in factors if f.get("_c_synth"))
        n = len(factors)

        # A3: Active Exposure (f.a) populated for all factors
        if with_a == n:
            out.append((PASS, "A3 RiskM Active Exposure",
                        f"{with_a}/{n} factors populated"))
        elif with_a >= n * 0.7:
            missing = [f["n"] for f in factors if f.get("a") is None]
            out.append((PART, "A3 RiskM Active Exposure",
                        f"{with_a}/{n} populated. Missing: {', '.join(missing[:5])}{'…' if len(missing)>5 else ''}"))
        else:
            out.append((FAIL, "A3 RiskM Active Exposure",
                        f"only {with_a}/{n} factors populated"))

        # NEW: portfolio raw exposure (f.e)
        if with_e == n:
            out.append((PASS, "NEW Portfolio absolute exposure (f.e)",
                        f"{with_e}/{n} factors populated"))
        elif with_e > 0:
            out.append((PART, "NEW Portfolio absolute exposure (f.e)",
                        f"{with_e}/{n} populated"))
        else:
            out.append((FAIL, "NEW Portfolio absolute exposure (f.e)",
                        "f.e is null across all factors"))

        # NEW: benchmark absolute exposure (f.bm) — explicitly added in this call
        if with_bm == n:
            out.append((PASS, "NEW Benchmark absolute exposure (f.bm)",
                        f"{with_bm}/{n} factors populated"))
        elif with_bm > 0:
            out.append((PART, "NEW Benchmark absolute exposure (f.bm)",
                        f"{with_bm}/{n} populated"))
        else:
            out.append((FAIL, "NEW Benchmark absolute exposure (f.bm)",
                        "f.bm is null — was supposed to land this call"))

        # A4: per-factor TE % (f.c) populated and NOT synthesized
        if synth_c == 0 and with_c == n:
            out.append((PASS, "A4 Per-factor TE % (no synthesis)",
                        f"{with_c}/{n} factors populated, no _c_synth markers"))
        elif synth_c > 0:
            out.append((PART, "A4 Per-factor TE %",
                        f"{with_c}/{n} have c, but {synth_c} are synthesized — need real values"))
        else:
            out.append((FAIL, "A4 Per-factor TE %",
                        f"only {with_c}/{n} factors have c"))

    # ---- A5: group-table completeness (bench sum ≈ 100%) ----
    for label, group in [("Sectors", sectors), ("Countries", countries), ("Regions", regions)]:
        if not group:
            continue
        bench_sum = sum(g.get("b") or 0 for g in group)
        if 95 <= bench_sum <= 105:
            out.append((PASS, f"A5 {label} bench coverage",
                        f"{len(group)} {label.lower()}, bench sum = {bench_sum:.1f}%"))
        elif bench_sum > 50:
            out.append((PART, f"A5 {label} bench coverage",
                        f"bench sum only {bench_sum:.1f}% (expected ~100%)"))
        else:
            out.append((FAIL, f"A5 {label} bench coverage",
                        f"bench sum only {bench_sum:.1f}% — group filter not removed?"))

    # ---- A6: Overall rank quintile grouping ----
    ranks = strat.get("ranks") or {}
    overall = None
    for key in ("over", "overall", "Overall"):
        if key in ranks and isinstance(ranks[key], list):
            overall = ranks[key]
            break
    if overall and len(overall) >= 5:
        # Each quintile should have OVER_WAvg matching its quintile number
        offsets = []
        for i, q in enumerate(overall[:5], 1):
            wa = q.get("over_wavg") or q.get("OVER_WAvg") or q.get("avg")
            if wa is not None:
                offsets.append(abs(wa - i))
        if offsets and max(offsets) < 0.05:
            out.append((PASS, "A6 Overall rank quintile grouping",
                        f"Q1=1.00, Q2=2.00, ... Q5=5.00 (max offset {max(offsets):.2f})"))
        elif offsets:
            out.append((FAIL, "A6 Overall rank quintile grouping",
                        f"Q1-Q5 offsets too large: {[f'{o:.2f}' for o in offsets]}"))
        else:
            out.append((PART, "A6 Overall rank quintile grouping",
                        "could not extract OVER_WAvg per quintile"))
    else:
        out.append((PART, "A6 Overall rank quintile grouping",
                    "ranks structure not in expected shape — verify manually"))

    # ---- A7: CSV quoting (heuristic — skipped without raw CSV) ----
    if csv_text is not None:
        # Look for any row where a comma-in-name column-shifted the row
        shifted = 0
        for line in csv_text.split("\n")[:5000]:
            # Simple heuristic: count commas; if a row has dramatically more than median, suspect
            pass  # Skipping detailed implementation; manual check needed
        out.append((PART, "A7 CSV quoting", "raw-CSV scan deferred — manual spot check required"))
    else:
        out.append((DIM + "—" + RESET, "A7 CSV quoting", "skipped (no CSV path provided)"))

    # ---- C1: Brinson inputs (already covered by per-holding period return) ----
    has_sec_ret = any(s.get("ret") is not None or s.get("r") is not None for s in sectors)
    bench_total_ret = summary.get("bench_total_return") or summary.get("bench_ret")
    if r_count >= total_rows * 0.5 or has_sec_ret or bench_total_ret:
        out.append((PASS, "C1 Brinson inputs",
                    f"per-holding return on {r_count} rows" + (f", bench_total_return={bench_total_ret}" if bench_total_ret else "")))
    else:
        out.append((FAIL, "C1 Brinson inputs",
                    "no per-holding period return, no per-sector return, no bench total return"))

    # ---- C2: % of Variance per 18 Style Snapshot row ----
    sample_factor = factors[0] if factors else None
    if sample_factor and ("pct_var" in sample_factor or "pctvar" in sample_factor or "variance_pct" in sample_factor):
        out.append((PASS, "C2 % of Variance per snapshot row",
                    "field present on factor rows"))
    else:
        out.append((FAIL, "C2 % of Variance per snapshot row",
                    "not added to 18 Style Snapshot rows"))

    # ---- C3: sector-level historical fields ----
    hist_sec = (strat.get("hist") or {}).get("sec") or {}
    if hist_sec and len(hist_sec) > 5:
        out.append((PASS, "C3 Sector historical fields",
                    f"hist.sec has {len(hist_sec)} sectors with history"))
    elif hist_sec:
        out.append((PART, "C3 Sector historical fields",
                    f"hist.sec has only {len(hist_sec)} sectors"))
    else:
        out.append((FAIL, "C3 Sector historical fields",
                    "hist.sec is empty"))

    # ---- C4: top-10 fundamentals ----
    chars_metrics = {c.get("m", ""): c for c in chars}
    fundamental_targets = [
        "Forward P/E", "P/E (NTM)", "Price/Earnings (NTM)",
        "EV/EBITDA", "Price/Sales", "P/S",
        "Revenue Growth 1Y", "ROIC",
        "Net Debt/EBITDA", "Total Return 1Y",
        "Excess Return", "Gross Margin",
        "EPS Growth NTM",
    ]
    found_funds = [t for t in fundamental_targets if any(t.lower() in k.lower() for k in chars_metrics)]
    if len(found_funds) >= 8:
        out.append((PASS, "C4 Top-10 fundamentals",
                    f"{len(found_funds)} of 13 target metrics present"))
    elif len(found_funds) >= 4:
        out.append((PART, "C4 Top-10 fundamentals",
                    f"only {len(found_funds)} target metrics found"))
    else:
        out.append((FAIL, "C4 Top-10 fundamentals",
                    f"only {len(found_funds)} target metrics found"))

    # ---- Bench P/E + P/B regression check ----
    pe = chars_metrics.get("Price/Earnings (P/E)") or chars_metrics.get("Forward P/E (NTM)")
    pb = chars_metrics.get("Price/Book (P/B)")
    if pe and pe.get("b") is not None:
        out.append((PASS, "Re-flag: Bench P/E populated",
                    f"port={pe.get('p')}, bench={pe.get('b')}"))
    else:
        out.append((FAIL, "Re-flag: Bench P/E populated",
                    "still null — confirmed-then-regressed; raise immediately if shipping"))
    if pb and pb.get("b") is not None:
        out.append((PASS, "Re-flag: Bench P/B populated",
                    f"port={pb.get('p')}, bench={pb.get('b')}"))
    else:
        out.append((FAIL, "Re-flag: Bench P/B populated", "still null"))

    # ---- C5: Hit rate ----
    hr = summary.get("hit_rate") or summary.get("hitrate")
    if hr is not None or any("hit" in c.get("m", "").lower() for c in chars):
        out.append((PASS, "C5 Hit rate / batting average", f"value={hr}" if hr is not None else "in chars"))
    else:
        out.append((PART, "C5 Hit rate / batting average", "not present (was 'nice-to-have')"))

    # ---- C6: trailing returns by horizon ----
    horizon_keys = ["ret_1m", "ret_3m", "ret_6m", "ret_1y", "ret_3y", "ret_5y", "return_1m", "return_3m", "return_1y"]
    hor_present = sum(1 for k in horizon_keys if summary.get(k) is not None)
    chars_horizons = sum(1 for c in chars if any(h in (c.get("m") or "").lower() for h in ["1m", "3m", "6m", "1y return", "3y return"]))
    if hor_present >= 3 or chars_horizons >= 3:
        out.append((PASS, "C6 Trailing returns by horizon",
                    f"{max(hor_present, chars_horizons)} horizons present"))
    else:
        out.append((PART, "C6 Trailing returns",
                    "few or no horizon-based return fields"))

    # ---- F7 verify still: snap_attrib granular ----
    if len(snap_attrib) > 50:
        out.append((PASS, "F7 snap_attrib granular keys",
                    f"{len(snap_attrib)} keys"))
    else:
        out.append((PART, "F7 snap_attrib", f"only {len(snap_attrib)} keys"))

    return out


def render_results(strat_id, results_list):
    sub(f"Strategy: {BOLD}{strat_id}{RESET}")
    counts = {PASS: 0, PART: 0, FAIL: 0}
    for status, name, msg in results_list:
        line = f"  {status} {name}"
        if msg:
            line += f"  {DIM}{msg}{RESET}"
        print(line)
        if status in counts:
            counts[status] += 1
    return counts


def main():
    json_path = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/RR/latest_data.json")
    csv_path = sys.argv[2] if len(sys.argv) > 2 else find_default_csv()

    if not os.path.exists(json_path):
        print(f"{RED}ERROR: {json_path} not found{RESET}")
        print(f"Run ./load_data.sh first.")
        sys.exit(1)

    header(f"FactSet test-pull verification — {json_path}")
    print(f"{DIM}CSV source: {csv_path or 'not provided'}{RESET}")

    data = load_json(json_path)

    # Format detection — RR JSON is `[strategies_dict, [], date_str, metadata_dict]`
    strategies = None
    if isinstance(data, list) and len(data) >= 1 and isinstance(data[0], dict):
        # Top-level is the array form
        strategies_dict = data[0]
        if any(isinstance(v, dict) and "hold" in v for v in strategies_dict.values()):
            strategies = strategies_dict
            metadata = data[3] if len(data) >= 4 and isinstance(data[3], dict) else {}
            if metadata:
                print(f"{DIM}Parser v{metadata.get('parser_version')} · format v{metadata.get('format_version')} · {metadata.get('total_rows')} rows · {metadata.get('file_size_mb')} MB{RESET}")
    elif isinstance(data, dict) and any(isinstance(v, dict) and "hold" in v for v in data.values()):
        strategies = data
    elif isinstance(data, dict) and "hold" in data:
        strategies = {"single": data}

    if not strategies:
        print(f"{RED}ERROR: Unexpected JSON shape{RESET}")
        print(f"  Top-level type: {type(data).__name__}")
        if isinstance(data, list):
            print(f"  List length: {len(data)}")
        sys.exit(1)

    csv_text = None  # reading 30+MB CSV is slow; only if needed for A7 deep check

    all_counts = {PASS: 0, PART: 0, FAIL: 0}
    fails_by_name = {}
    for strat_id, strat in strategies.items():
        if not isinstance(strat, dict) or "hold" not in strat:
            continue
        results_list = check_strategy(strat_id, strat, csv_text)
        counts = render_results(strat_id, results_list)
        for k, v in counts.items():
            all_counts[k] += v
        # Aggregate failures
        for status, name, msg in results_list:
            if status == FAIL:
                fails_by_name.setdefault(name, []).append(strat_id)

    # ---- Summary ----
    header("VERDICT")
    total = sum(all_counts.values())
    print(f"\n  {PASS} Pass:   {BOLD}{all_counts[PASS]}{RESET}")
    print(f"  {PART} Partial: {BOLD}{all_counts[PART]}{RESET}")
    print(f"  {FAIL} Fail:   {BOLD}{all_counts[FAIL]}{RESET}")
    print(f"  Total checks: {total}\n")

    if fails_by_name:
        print(f"{BOLD}{RED}FAILURES NEEDING FACTSET FOLLOW-UP:{RESET}\n")
        for name, strats in fails_by_name.items():
            print(f"  {FAIL} {name}  {DIM}({len(strats)} strateg{'y' if len(strats)==1 else 'ies'}){RESET}")

    print()
    if all_counts[FAIL] == 0 and all_counts[PART] <= 2:
        print(f"{BOLD}{GREEN}🟢 GREEN-LIGHT — all critical checks pass{RESET}")
        print(f"   Massive run can proceed.")
        return 0
    elif all_counts[FAIL] == 0:
        print(f"{BOLD}{YELLOW}🟡 GREEN-LIGHT WITH NOTES — partials are 'nice-to-have', no blockers{RESET}")
        print(f"   {all_counts[PART]} partial item(s) noted but none block the massive run.")
        return 0
    else:
        print(f"{BOLD}{RED}🔴 FIX REQUIRED — {all_counts[FAIL]} blocking check(s) failed{RESET}")
        print(f"   Send the failure list above back to FactSet before authorizing the massive run.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
