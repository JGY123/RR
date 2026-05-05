# FactSet × Claude Integration — Strategic Watch

**Drafted:** 2026-05-05
**Trigger:** user attended FactSet Focus conference; saw demo / announcement that Claude is being integrated directly into FactSet Workstation (FDS), with availability targeted for **June 2026**.
**Status:** monitoring. NOT pivoting current Alger VM deployment plan. Capturing strategic context so future sessions inherit the thinking.

---

## 1. What we heard

FactSet announced Claude integration into FDS, expected to open up in June. The user's interpretation: we could take RR code from git, drop it inside FactSet's environment, and from there have direct access to FactSet's full data — bypassing the CSV export → parser → JSON pipeline entirely.

**Source:** verbal report from FactSet Focus conference (no link / press release URL captured yet). Confirm details before relying on.

---

## 2. Why this matters (potentially)

If the integration lands as the user described, it changes 5 things:

| Today | Potential June+ |
|---|---|
| CSV export → Alger script → parser → JSON → dashboard | Direct FactSet API → dashboard runs inside FactSet (or alongside) |
| Re-extracts are resource-constrained ⇒ backup discipline drives architecture | Re-extracts cheap/free ⇒ backup posture relaxes |
| Weekly cadence | Real-time / on-demand possible |
| Multi-firm rollout = duplicated infra per firm | Multi-firm = one dashboard, any FDS client uses it |
| Parser is the source-of-truth gate | Parser becomes optional / fallback |

If the integration is more limited (e.g., Claude-as-chat-assistant inside FDS, no custom-app hosting, no programmatic data API), most of the table above doesn't apply. **We don't know which scenario yet.**

---

## 3. What does NOT change regardless

- **Anti-fabrication discipline** — about correctness, not about ingest path
- **Audit cadence** — still applies tile-by-tile
- **Defensive UI** — F18 footers, ᵉ markers, em-dash for missing data
- **The dashboard's value prop** — cross-strategy synthesis, F12(a) provenance, etc.
- **The Alger VM deployment plan as v1** — June is 1 month out; conference demos can be aspirational

These are the things RR earns regardless of where it runs.

---

## 4. Why we're NOT pivoting the current plan

1. **Conference demos ≠ production.** "Open to use in June" could mean preview / limited beta / rate-limited / multi-month rollout. Until Alger has confirmed early access, treat as roadmap not commit.
2. **Deployment model is unclear.** Five plausible interpretations:
   - (a) Claude embedded as a chat assistant in FDS — answers questions; no custom apps
   - (b) Custom-app hosting INSIDE FDS — RR could ship as an embedded iframe / canvas
   - (c) Claude has API access to FactSet data; user's apps elsewhere can query through it
   - (d) FDS gets a new Python notebook surface, Claude can write code in it
   - (e) Some mix
   Each implies a very different RR architecture. We can't design for all five.
3. **Alger needs RR working THIS quarter.** PMs are about to use it. Waiting on FactSet integration risks a launch slip and breaks the pre-FactSet-integration trust we've built ("the dashboard works today, here's what's in it").
4. **Forking is cheap.** RR's static HTML + CSS variables + Plotly + ARCHITECTURE-documented contract ports cleanly. The discipline travels. Whatever architecture FactSet offers, RR adapts.

---

## 5. The two-track strategy

### Track A — v1 (ship now)

Continue per `ALGER_DEPLOYMENT.md` + `LAUNCH_PLAN.md`:
- Linux VM in Alger's environment hosts RR
- Ingest pipeline is the existing `load_multi_account.sh --merge` chain
- PMs access via internal URL on Alger's network
- Backup strategy as-designed

**Status:** in progress. Target completion before Alger's PMs start using it (timeline TBD by Alger IT).

### Track B — v2 (watch, don't build)

When concrete details land:
- 30-min FactSet call to ask the 8 questions in §7 below
- Decide: full migration / hybrid / no change
- If hybrid or migration: a 1-2 week design sprint to evaluate

**Status:** monitoring. No engineering effort yet.

---

## 6. What v2 might look like (each scenario)

### Scenario A — Claude is a chat assistant inside FDS, custom apps not supported

**Implication:** RR architecture unchanged. PMs use both surfaces:
- RR for structured single-pane synthesis (the dashboard)
- Claude-in-FDS for ad-hoc questions ("explain why TE moved this week", "summarize this week's factor rotation")

**Action:** add a "ask Claude in FDS" link in RR's `?` button → deep-link to FDS Claude with context pre-populated.

### Scenario B — Custom-app hosting inside FDS

**Implication:** RR can be embedded as a canvas in FDS. Major win.
- Migrate RR static HTML to FDS canvas hosting
- Replace CSV ingest with direct FactSet API calls (skip parser)
- Per-PM auth via FactSet's existing user system
- Multi-firm: any Alger client gets RR by default

**Action:** 1-2 week migration sprint. Most of RR's HTML + CSS + Plotly should port. Parser stays in repo as fallback / dev tool.

### Scenario C — Programmatic API only, no UI hosting

**Implication:** RR stays hosted on Alger VM, but the ingest pipeline can pull directly from FactSet's API instead of consuming CSVs.
- Replace `load_multi_account.sh` CSV ingest with API calls
- Eliminate the manual CSV-export step
- Real-time updates possible

**Action:** rewrite the ingest layer (~1 week). Dashboard unchanged.

### Scenario D — Python notebook + Claude

**Implication:** Power users (analysts, the user) get a notebook surface to do bespoke analysis on top of RR's data + the wider FactSet universe. PMs still use the dashboard.

**Action:** publish RR's data schemas + a starter notebook template for analysts.

### Scenario E — Some mix

Most likely. Decompose into the components above.

---

## 7. Questions to ask FactSet (when the right person is available)

Stale until we have a contact. The user can drop these into a single email or a 30-min call agenda.

1. **Deployment model:** can we deploy a static HTML + JS + Plotly dashboard inside the FDS workstation, or is the integration limited to Claude-as-chat?
2. **Data API surface:** can we query Portfolio Attribution data programmatically through Claude / through a regular API / through a notebook? Auth model? Rate limits? Cost?
3. **User auth:** per-user (each PM authenticates to FDS separately) or per-org (Alger gets org-level access)?
4. **Data freshness:** real-time / intraday / EOD / weekly?
5. **Custom code execution:** can our existing Plotly + JS render inside FDS, or is execution limited to FactSet's stack?
6. **Off-FDS access:** if we deploy inside FDS, can users still access the dashboard without an FDS license? (Compliance / audit concern.)
7. **June rollout scope:** is Alger eligible for early access? Public beta vs general availability? Geofence?
8. **Pricing model:** seat-based (each FDS user pays), data-volume-based (per query / row), or bundled?

Bonus questions if time:

- Are there existing FactSet customers running custom dashboards inside FDS today (not via Claude)? What's the precedent?
- Does the integration support batch / scheduled jobs (e.g., a weekly RR refresh runs without a logged-in user)?
- What's the data-retention model? If we leave RR running and a PM opens it 6 months later, does FactSet still have the underlying data?
- Roadmap: what comes AFTER June? (To avoid building for a transient surface.)

---

## 8. Decision triggers — when to pivot

Pivot Track B → primary if any of these become true:

- **FactSet announces concrete custom-app hosting** with a documented deployment path — pivot to Scenario B if effort ≤ 2 weeks
- **Alger's IT proposes RR-in-FDS** as their preferred deployment model
- **A second firm** (i.e., not Alger) wants RR — multi-firm value of FDS hosting is too good to pass up
- **CSV export becomes harder** (FactSet deprecates the export, or pricing changes against us) — forces the API path

Stay on Track A if:
- The integration is chat-only (Scenario A)
- Custom-app hosting is too constrained (e.g., no JS, no localStorage, no Plotly)
- Pricing makes per-PM access unaffordable
- Alger doesn't get early access until late 2026

---

## 9. Pre-emptive design notes for v2 (if we do migrate)

If/when we know we're going to FactSet hosting, the things that make the migration easier:

- **Keep the parser as a documented contract.** Even if we eventually call FactSet's API directly, the parser's output schema (FORMAT_VERSION 4.3) is the dashboard's input contract. The dashboard doesn't care where the data comes from as long as it matches the schema.
- **Keep CSS-variable-driven theming.** Whatever environment hosts RR will have its own brand expectations; the theme system handles that.
- **Keep `data/strategies/<ID>.json` as the data layer.** If FactSet hosting comes with a real-time API, the rendering layer can fetch on-demand and write to this same shape — the rest of the app stays unchanged.
- **Don't ship features that depend on Alger-VM-specifics** (e.g., absolute filesystem paths, cron-only flows, network-internal-only assumptions). The current architecture mostly avoids this; just stay disciplined.

---

## 10. Closing

This is real news, potentially transformative, but the right move today is: **complete the Alger VM deployment, treat FactSet/Claude as a v2 path to evaluate when concrete details emerge.**

The discipline that makes RR valuable (anti-fabrication, audit cadence, defensive UI) ports cleanly to whatever environment ends up hosting it. Don't defer launch on speculation; don't ignore the option either.

Re-read this doc when:
- Concrete FactSet/Claude integration details land (probably April-June 2026 cadence)
- Alger's IT proposes a different deployment model
- A 2nd firm asks about RR
