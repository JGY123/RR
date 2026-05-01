# Universe Selector Audit — "Both" Logic Investigation

**Triggered by:** User feedback (2026-05-01): _"At the top-level universe selector, there are options for Portfolio, Benchmark, and Both. I am not fully clear what 'Both' is doing. Based on checking the security counts, it looks like either 'Both' is problematic, or the benchmark selection also has an issue."_

**Methodology:** Audit `aggregateHoldingsBy(holds, …, {mode})` at line 4466. Trace which fields the universe filter gates, run a numerical check on ACWI to see what the user is seeing.

---

## How the code defines each mode

```js
const inUniverse = mode==='both'
  || (mode==='portfolio'&&((+h.p)>0))
  || (mode==='benchmark'&&((+h.b)>0));
```

- **`portfolio`** = holdings with portfolio weight > 0 (i.e., port-held)
- **`benchmark`** = holdings with benchmark weight > 0 (i.e., bench-listed) — this **includes** stocks that are also in the portfolio
- **`both`** = no filter — every non-cash holding regardless of weight

`inUniverse` gates: **count**, port-weight sum, bench-weight sum, active-weight sum, ORVQ rank averages.

**`tr` / `mcr` / `factor_contr` — always aggregated, NEVER gated by universe** (this was the B116 fix, 2026-04-30: TE is a single answer, the Universe pill must not move it).

## What the user sees on ACWI (2048 holdings)

| Mode | Count | Behavior |
|---|---:|---|
| **Portfolio** | 39 | port-held only (`h.p > 0`) |
| **Benchmark** | ~2048 | every constituent of MSCI ACWI (`h.b > 0`) — **includes** the 39 port-held overlap |
| **Both** | 2048 | union of port-held + bench-listed = nearly identical to Benchmark in this case |

## Why "Bench ≈ Both"

For a portfolio that is a strict subset of its benchmark (the typical case), the bench universe is huge (1,500-2,500 names) and the portfolio is small (30-50 names). Almost every port-held name is also in the benchmark. So:

- `Bench` mode = all benchmark constituents = port-held overlap (~39) + bench-only (~2,009) = **2,048**
- `Both` mode = union = same set = **2,048**

The two are mathematically identical when no holdings are pure-port (i.e., port-held but not in benchmark — rare for diversified strategies).

## Is there a bug?

**No double-counting.** Each holding is counted exactly once in any mode. The aggregation iterates `holds` once and applies the filter; no holding contributes twice.

**However, the user's instinct is right that something is off — but not as a bug. As a UX/labeling problem:**

1. **"Both" implies "Port + Bench" arithmetically.** Users expect `Both = Port_count + Bench_count`. They get the union (which equals Bench when Port ⊂ Bench). When `Port = 39`, `Bench = 2048`, intuition says `Both = 2087`. Reality says `Both = 2048`. Off by 39.

2. **"Benchmark" is ambiguous.** It currently means "every stock in the benchmark including overlap." Users may read it as "bench-ONLY" (i.e., names in benchmark NOT in portfolio). That'd give `Bench-only = 2,009`. Different number.

3. **`tr` / `mcr` / `factor_contr` are universe-invariant** — the user-visible TE Contrib columns DON'T change when toggling Port → Bench → Both. Only count, port wt, bench wt, active wt, ORVQ averages change. This is correct (TE is a single objective truth) but may confuse users who expect TE to track the toggle.

## Recommendations (no code yet, awaiting your call)

| Option | Description | Pros | Cons |
|---|---|---|---|
| **A.** Rename pills | `Port` → `Port-Held`, `Bench` → `In Benchmark`, `Both` → `All Holdings` | Zero risk. Just labels. | Doesn't fully address the underlying ambiguity. |
| **B.** Drop "Both" | Hide it. Most users only need Port vs Bench. | Cleanest. | Loses ability to see e.g. portfolio + bench-only ranks together. |
| **C.** Add "Bench-Only" | New pill: `Port` / `Bench` / `Bench-Only` / `All`. Bench-Only filters `h.b > 0 && h.p === 0`. | Disambiguates. | More pills. Mild visual clutter. |
| **D.** Hover tooltip on each pill | Show the count it would produce ("Port: 39 names · Bench: 2048 names · Both: 2048 names") | Lowest cost, makes confusion impossible. | Doesn't fix the labels. |
| **E.** Status strip below pills | Persistent caption: "Universe = Bench (2,048 names · 1,489 with b>0 · 39 port-held overlap)" | Always visible. Educates. | More chrome. |

**My recommended combo:** **A + D + E** → rename for clarity, hover tooltips for fast disambiguation, persistent status strip so the user always knows what's selected.

**Risk if I change anything:** ZERO data risk if just labels/tooltips/strip. Behavior unchanged.

---

## Final verdict

**No double-counting bug.** The math is correct. The confusion is in **what the labels mean** + **what the user expects them to mean**. This is a UX problem, not a data problem.

**Awaiting your call on which option (or combo) to ship.**
