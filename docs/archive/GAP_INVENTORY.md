# GAP_INVENTORY — RR Dashboard Feature Reconciliation (gap-discovery.v1)

> Systematic pre-crisis feature reconciliation. Auto-generated 2026-04-16 by mining
> ~25 JSONL conversation transcripts (27,011 lines, ~239MB), 5 tile-spec
> conversation logs (~1.4MB each), the `backup-all-today-work` branch baseline,
> TILE_SPEC.md's 29-tile inventory, CLAUDE.md's feature list, and 29 cli-prompts
> patch files. Each row traces back to a concrete source (JSONL file:line,
> branch, or doc path). See ~/RR/GAP_DISCOVERY.md for methodology.

## Methodology

- **Mining pass:** Parsed every JSONL line; extracted every `tool_use: Write|Edit|MultiEdit`
  targeting `dashboard_v7.html`. From each write's content, captured function definitions,
  `id="…"` attributes, `onclick="handler(…)"` handlers, `.card-title` text, and
  `localStorage.setItem('rr_…')` keys.
- **Classification:** Each feature grepped against `dashboard_v7.html` HEAD and
  `backup-all-today-work:dashboard_v7.html` to determine present / missing / regressed.
- **Doc enrichment:** Added 29 tile-level features from TILE_SPEC.md (Tiers 1–5 + drill
  modals), 12 feature-bullets from CLAUDE.md, and 24 planned-patch features from
  `cli-prompts/*.md`.
- **Priority:** Heuristic score combining refcount, kind (card-title/onclick outrank
  helpers), workflow keywords (hold/sector/factor/threshold/treemap), and regressed
  status.

## Summary Stats

- **Total rows:** 860
- **Present (✅):** 513
- **Missing (❌):** 325  (of which **regressed since backup:** 68)
- **Unclear (🤷):** 22
- **High-priority missing:** 14
- **Medium-priority missing:** 91

---

## Inventory

Rows are grouped by feature area. Sources are truncated to first 3 JSONL hits;
full ref counts in parentheses.


### attribution

| Feature | Source(s) | Status | Priority | Notes |
|---|---|---|---|---|
| `Factor Attribution — Return Impact` (card-title) | 0306b5a0-0173-4ce1-8e03-64e3cca07936.jsonl:L653, 0f6b5a8f-d645-4fb2-8123-64f4d239f8ce.jsonl:L117, 0f6b5a8f-d645-4fb2-8123-64f4d239f8ce/subagents/agent-acompact-840fe4766c4084ee.jsonl:L89 (×5) | ✅ present (new) | high |  |
| 18 Style Snapshot Granular Data Integration | cli-prompts/snap-attrib-integration-patch.md | ❌ missing | medium |  |
| `genAttrib` (function) | 9bb62f73-0e91-4b88-8263-95e8523b2238.jsonl:L414, 9bb62f73-0e91-4b88-8263-95e8523b2238/subagents/agent-acompact-fa5af12711981885.jsonl:L54 (×2) | ❌ missing (regressed) | medium |  |
| `setAttribPeriod` (function) | 0306b5a0-0173-4ce1-8e03-64e3cca07936.jsonl:L567, 0306b5a0-0173-4ce1-8e03-64e3cca07936.jsonl:L657, 0306b5a0-0173-4ce1-8e03-64e3cca07936.jsonl:L916 (×3) | ❌ missing | medium |  |
| `setAttribPeriod` (onclick) | 0306b5a0-0173-4ce1-8e03-64e3cca07936.jsonl:L570, 0306b5a0-0173-4ce1-8e03-64e3cca07936.jsonl:L653, 0306b5a0-0173-4ce1-8e03-64e3cca07936.jsonl:L866 (×4) | ❌ missing | medium |  |
| `tab-attribution` (id) | 0f6b5a8f-d645-4fb2-8123-64f4d239f8ce.jsonl:L68, 0f6b5a8f-d645-4fb2-8123-64f4d239f8ce/subagents/agent-acompact-840fe4766c4084ee.jsonl:L54 (×2) | ❌ missing (regressed) | medium |  |
| Multi-Period Attribution Dashboard | cli-prompts/multi-period-attribution-patch.md | ❌ missing | medium |  |
| `Factor Attribution` (card-title) | 0306b5a0-0173-4ce1-8e03-64e3cca07936.jsonl:L570 | ✅ present | medium |  |
| `oDrAttrib` (onclick) | 0306b5a0-0173-4ce1-8e03-64e3cca07936.jsonl:L573, bf250eb0-8cb6-4c32-96f7-d26d443c8a97.jsonl:L696, bf250eb0-8cb6-4c32-96f7-d26d443c8a97.jsonl:L833 (×4) | ✅ present | medium |  |
| `tbl-attrib` (id) | 0306b5a0-0173-4ce1-8e03-64e3cca07936.jsonl:L1597, 0306b5a0-0173-4ce1-8e03-64e3cca07936.jsonl:L1602, 0306b5a0-0173-4ce1-8e03-64e3cca07936.jsonl:L573 (×3) | ✅ present (new) | medium |  |
| Factor Attribution — 18 Style Snapshot (cardAttrib) | TILE_SPEC.md Tier 4 #19 | ✅ present | medium |  |
| Factor Attribution — Return Impact Waterfall | TILE_SPEC.md Tier 4 #18 | 🤷 unclear | medium |  |
| `attribPeriodImp` (function) | 0306b5a0-0173-4ce1-8e03-64e3cca07936.jsonl:L567, 0306b5a0-0173-4ce1-8e03-64e3cca07936.jsonl:L916 (×2) | ❌ missing | low |  |
| `tabAttribution` (id) | 6790f467-65e5-4043-923d-14cd2da4c529.jsonl:L1287, 6790f467-65e5-4043-923d-14cd2da4c529/subagents/agent-acompact-51ea98d896d5f5d7.jsonl:L159 (×2) | ❌ missing | low |  |
| `attribCategory` (id) | 0306b5a0-0173-4ce1-8e03-64e3cca07936.jsonl:L570 | ✅ present (new) | low |  |
| `cardAttrib` (id) | bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompact-2b2e69850cfd4eef.jsonl:L204 | ✅ present | low |  |
| `FactSet Attribution — ${name}` (card-title) | bf250eb0-8cb6-4c32-96f7-d26d443c8a97.jsonl:L2465, f168094b-9d6e-466e-ba15-6b0f8cbc7c6e.jsonl:L55 (×2) | ✅ present (new) | low |  |
| `oDrAttrib` (function) | bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompact-2b2e69850cfd4eef.jsonl:L59 | ✅ present | low |  |

### beta

| Feature | Source(s) | Status | Priority | Notes |
|---|---|---|---|---|
| `Beta History` (card-title) | 0f6b5a8f-d645-4fb2-8123-64f4d239f8ce.jsonl:L128, 0f6b5a8f-d645-4fb2-8123-64f4d239f8ce/subagents/agent-acompact-840fe4766c4084ee.jsonl:L97, b2861e29-fdab-4386-a79d-886c89059725.jsonl:L133 (×6) | ✅ present (new) | high |  |
| `Beta — Predicted · Historical · MPT` (card-title) | 33df0d54-3b91-47b9-8d9b-71ad1f12c0c9.jsonl:L126 | ❌ missing (regressed) | medium |  |
| `Beta History — Predicted` (card-title) | b7818bde-fbfd-4187-a4c0-2518a1e4cbd0.jsonl:L120, b7818bde-fbfd-4187-a4c0-2518a1e4cbd0.jsonl:L164 (×2) | ✅ present (new) | medium |  |
| `riskBetaMultiDiv` (id) | 0f6b5a8f-d645-4fb2-8123-64f4d239f8ce.jsonl:L128, 0f6b5a8f-d645-4fb2-8123-64f4d239f8ce/subagents/agent-acompact-840fe4766c4084ee.jsonl:L97, b2861e29-fdab-4386-a79d-886c89059725.jsonl:L133 (×8) | ✅ present (new) | medium |  |
| `rMultiBeta` (function) | 9bb62f73-0e91-4b88-8263-95e8523b2238.jsonl:L152, 9bb62f73-0e91-4b88-8263-95e8523b2238/subagents/agent-acompact-5d03aa71ce7b3960.jsonl:L150, 9bb62f73-0e91-4b88-8263-95e8523b2238/subagents/agent-aside_q… (×7) | ✅ present (new) | medium |  |
| Beta History Chart (Risk inline) | TILE_SPEC.md Tier 4 #20 | 🤷 unclear | medium |  |
| `All Beta Measures` (card-title) | bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompact-2b2e69850cfd4eef.jsonl:L349 | ❌ missing | low |  |
| `miniBeta` (id) | 6790f467-65e5-4043-923d-14cd2da4c529.jsonl:L1416, 6790f467-65e5-4043-923d-14cd2da4c529/subagents/agent-acompact-51ea98d896d5f5d7.jsonl:L265 (×2) | ❌ missing | low |  |
| `multiBetaDiv` (id) | 33df0d54-3b91-47b9-8d9b-71ad1f12c0c9.jsonl:L126 | ❌ missing (regressed) | low |  |
| `Beta Measures — click to overlay on chart` (card-title) | bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompact-2b2e69850cfd4eef.jsonl:L375 | ✅ present | low |  |
| `toggleBetaOverlay` (function) | bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompact-2b2e69850cfd4eef.jsonl:L378 | ✅ present | low |  |
| `toggleBetaOverlay` (onclick) | bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompact-2b2e69850cfd4eef.jsonl:L375 | ✅ present | low |  |

### cash

| Feature | Source(s) | Status | Priority | Notes |
|---|---|---|---|---|
| `thr_cashMax` (id) | 529c73ed-d7c3-4965-8e2a-33f7fef38298.jsonl:L63 | ✅ present (new) | low |  |

### compare

| Feature | Source(s) | Status | Priority | Notes |
|---|---|---|---|---|
| `Peer Comparison (${h.sec})` (card-title) | 6790f467-65e5-4043-923d-14cd2da4c529.jsonl:L770, 6790f467-65e5-4043-923d-14cd2da4c529/subagents/agent-acompact-31f87266afe462b7.jsonl:L18, bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompact… (×3) | ❌ missing (regressed) | medium |  |
| `compareBtn` (id) | 37b9aba8-d807-4adf-b672-764e27067d0e.jsonl:L76, bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompact-2b2e69850cfd4eef.jsonl:L178, bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompact… (×4) | ✅ present | medium |  |
| openComp — strategy comparison modal | TILE_SPEC.md drill modals | 🤷 unclear | medium |  |
| Strategy Comparison Mode | cli-prompts/strategy-comparison-patch.md | ✅ present | medium |  |

### context-menu

| Feature | Source(s) | Status | Priority | Notes |
|---|---|---|---|---|
| Right-click context menu for cell values | CLAUDE.md Features | ✅ present | medium |  |
| `closeMenu` (function) | fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L2024 | ❌ missing | low |  |

### correlation

| Feature | Source(s) | Status | Priority | Notes |
|---|---|---|---|---|
| `oDrCorr` (onclick) | b2861e29-fdab-4386-a79d-886c89059725.jsonl:L425, b2861e29-fdab-4386-a79d-886c89059725/subagents/agent-acompact-7d364f7476edf88e.jsonl:L266, bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompac… (×3) | ❌ missing (regressed) | medium |  |
| `rFCorr` (function) | b2861e29-fdab-4386-a79d-886c89059725.jsonl:L425, b2861e29-fdab-4386-a79d-886c89059725/subagents/agent-acompact-7d364f7476edf88e.jsonl:L266, bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompac… (×3) | ❌ missing (regressed) | medium |  |
| `corrMatrixWrap` (id) | 0f6b5a8f-d645-4fb2-8123-64f4d239f8ce.jsonl:L128, 0f6b5a8f-d645-4fb2-8123-64f4d239f8ce/subagents/agent-acompact-840fe4766c4084ee.jsonl:L97, b2861e29-fdab-4386-a79d-886c89059725.jsonl:L416 (×9) | ✅ present (new) | medium |  |
| `pearson` (function) | b2861e29-fdab-4386-a79d-886c89059725.jsonl:L425, b2861e29-fdab-4386-a79d-886c89059725.jsonl:L648, b2861e29-fdab-4386-a79d-886c89059725/subagents/agent-acompact-7d364f7476edf88e.jsonl:L266 (×7) | ✅ present (new) | medium |  |
| Factor Correlation Matrix full (Risk) | TILE_SPEC.md Tier 5 #26 | 🤷 unclear | medium |  |
| Factor Correlation Matrix preview (cardCorr) | TILE_SPEC.md Tier 5 #25 | ✅ present | medium | Marked Building |
| `calcCorrMatrix` (function) | 33df0d54-3b91-47b9-8d9b-71ad1f12c0c9.jsonl:L108 | ❌ missing (regressed) | low |  |
| `corrAll` (id) | 33df0d54-3b91-47b9-8d9b-71ad1f12c0c9.jsonl:L126 | ❌ missing (regressed) | low |  |
| `corrFQ` (id) | 33df0d54-3b91-47b9-8d9b-71ad1f12c0c9.jsonl:L126 | ❌ missing (regressed) | low |  |
| `corrGrpSortBtn` (id) | fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L2164, fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L2170, fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L2177 (×4) | ❌ missing | low |  |
| `corrMatrixDiv` (id) | 33df0d54-3b91-47b9-8d9b-71ad1f12c0c9.jsonl:L126 | ❌ missing (regressed) | low |  |
| `corrTF` (id) | 33df0d54-3b91-47b9-8d9b-71ad1f12c0c9.jsonl:L126 | ❌ missing (regressed) | low |  |
| `oDrCorr` (function) | bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompact-2b2e69850cfd4eef.jsonl:L59 | ❌ missing (regressed) | low |  |
| `pearsonCorr` (function) | 33df0d54-3b91-47b9-8d9b-71ad1f12c0c9.jsonl:L108 | ❌ missing (regressed) | low |  |
| `rRiskCorrDraw` (function) | 33df0d54-3b91-47b9-8d9b-71ad1f12c0c9.jsonl:L108, 33df0d54-3b91-47b9-8d9b-71ad1f12c0c9.jsonl:L212 (×2) | ❌ missing (regressed) | low |  |
| `corrMatrixCardArea` (id) | 9bb62f73-0e91-4b88-8263-95e8523b2238.jsonl:L1378, 9bb62f73-0e91-4b88-8263-95e8523b2238.jsonl:L1651 (×2) | ✅ present (new) | low |  |

### country

| Feature | Source(s) | Status | Priority | Notes |
|---|---|---|---|---|
| `Country Active Weights (Top OW / UW)` (card-title) | bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompact-2b2e69850cfd4eef.jsonl:L182 | ❌ missing (regressed) | medium |  |
| `Factor Contributions to Country TE` (card-title) | fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L838 | ❌ missing | medium |  |
| `oDrCountry` (onclick) | 9bb62f73-0e91-4b88-8263-95e8523b2238.jsonl:L752, 9bb62f73-0e91-4b88-8263-95e8523b2238/subagents/agent-acompact-f59e4390ac8d39a6.jsonl:L106, bf250eb0-8cb6-4c32-96f7-d26d443c8a97.jsonl:L1075 (×7) | ✅ present | medium |  |
| `rCountryTable` (function) | 9bb62f73-0e91-4b88-8263-95e8523b2238.jsonl:L752, 9bb62f73-0e91-4b88-8263-95e8523b2238/subagents/agent-acompact-f59e4390ac8d39a6.jsonl:L106, bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompac… (×4) | ✅ present | medium |  |
| Country Exposure (cardCountry) | TILE_SPEC.md Tier 3 #13 | ✅ present | medium |  |
| `cardCountryChart` (id) | bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompact-2b2e69850cfd4eef.jsonl:L182 | ❌ missing (regressed) | low |  |
| `cardCountryTable` (id) | bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompact-2b2e69850cfd4eef.jsonl:L182 | ❌ missing (regressed) | low |  |
| `coAvg` (function) | fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L728 | ❌ missing | low |  |
| `ctryHoldBarDiv` (id) | bf250eb0-8cb6-4c32-96f7-d26d443c8a97.jsonl:L2465, fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L838 (×2) | ❌ missing | low |  |
| `ctryRankAvg` (id) | fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L728 | ❌ missing | low |  |
| `ctryRankBM` (id) | fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L728 | ❌ missing | low |  |
| `ctryRankPort` (id) | fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L728 | ❌ missing | low |  |
| `ctryRankWtd` (id) | fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L728 | ❌ missing | low |  |
| `ctrySnapHistDiv` (id) | bf250eb0-8cb6-4c32-96f7-d26d443c8a97.jsonl:L2465 | ❌ missing | low |  |
| `oDrCtry` (onclick) | fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L2929 | ❌ missing | low |  |
| `regAvg` (function) | fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L732 | ❌ missing | low |  |
| `setCtryRankMode` (function) | fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L722 | ❌ missing | low |  |
| `setCtryRankSrc` (function) | fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L722 | ❌ missing | low |  |
| `cardCountry` (id) | 0306b5a0-0173-4ce1-8e03-64e3cca07936.jsonl:L1369, 0306b5a0-0173-4ce1-8e03-64e3cca07936.jsonl:L1373 (×2) | ✅ present (new) | low |  |
| `Country Exposure` (card-title) | fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L2967 | ✅ present (new) | low |  |
| `countryAttribChart` (id) | f168094b-9d6e-466e-ba15-6b0f8cbc7c6e.jsonl:L55 | ✅ present (new) | low |  |
| `countryChartDiv` (id) | bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompact-2b2e69850cfd4eef.jsonl:L182 | ✅ present | low |  |
| `countryContent` (id) | bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompact-2b2e69850cfd4eef.jsonl:L55, fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L825 (×2) | ✅ present | low |  |
| `countryModal` (id) | bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompact-2b2e69850cfd4eef.jsonl:L55, fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L825 (×2) | ✅ present | low |  |
| `oDrCountry` (function) | bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompact-2b2e69850cfd4eef.jsonl:L59, fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L838 (×2) | ✅ present | low |  |
| `rCountryMap` (function) | fbae49d0-369a-42ae-8bee-3fbd440690f7.jsonl:L399 | ✅ present (new) | low |  |
| `renderCountryAttribChart` (function) | f168094b-9d6e-466e-ba15-6b0f8cbc7c6e.jsonl:L55 | ✅ present (new) | low |  |
| `renderCountryAttribSection` (function) | f168094b-9d6e-466e-ba15-6b0f8cbc7c6e.jsonl:L55 | ✅ present (new) | low |  |
| `renderFsCountry` (function) | fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L2929 | ✅ present (new) | low |  |
| `tbl-ctry` (id) | 9bb62f73-0e91-4b88-8263-95e8523b2238.jsonl:L752, 9bb62f73-0e91-4b88-8263-95e8523b2238/subagents/agent-acompact-f59e4390ac8d39a6.jsonl:L106, bf250eb0-8cb6-4c32-96f7-d26d443c8a97.jsonl:L1086 (×4) | ✅ present (new) | low |  |
| `toggleCountryView` (function) | fbae49d0-369a-42ae-8bee-3fbd440690f7.jsonl:L1661 | ✅ present (new) | low |  |
| `toggleCountryView` (onclick) | fbae49d0-369a-42ae-8bee-3fbd440690f7.jsonl:L1625 | ✅ present (new) | low |  |

### distribution-ghost

| Feature | Source(s) | Status | Priority | Notes |
|---|---|---|---|---|
| `Rank Distribution` (card-title) | 875a1df5-d045-4fed-bd15-774cf1ce2337.jsonl:L174, 875a1df5-d045-4fed-bd15-774cf1ce2337/subagents/agent-acompact-36cc92af1a191d24.jsonl:L156, holdings-tab-spec.md:L68 (×3) | ✅ present | medium |  |
| `mkDistGhost` (function) | bf250eb0-8cb6-4c32-96f7-d26d443c8a97.jsonl:L1047, bf250eb0-8cb6-4c32-96f7-d26d443c8a97.jsonl:L1326 (×2) | ❌ missing | low |  |

### email-export

| Feature | Source(s) | Status | Priority | Notes |
|---|---|---|---|---|
| Email Report Generator | cli-prompts/email-report-patch.md | ❌ missing | high |  |
| `generateEmailSnapshot` (function) | 6790f467-65e5-4043-923d-14cd2da4c529.jsonl:L1352, 6790f467-65e5-4043-923d-14cd2da4c529.jsonl:L1356, 6790f467-65e5-4043-923d-14cd2da4c529/subagents/agent-acompact-51ea98d896d5f5d7.jsonl:L211 (×8) | ✅ present | high |  |
| `generateEmailSnapshot` (onclick) | 6790f467-65e5-4043-923d-14cd2da4c529.jsonl:L1341, 6790f467-65e5-4043-923d-14cd2da4c529/subagents/agent-acompact-51ea98d896d5f5d7.jsonl:L203, bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompa… (×5) | ✅ present | high |  |
| Email snapshot generation (holdings, tilts, OW/UW) | CLAUDE.md Features | 🤷 unclear | high |  |
| `emailPreviewModal` (id) | fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L1101, fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L1105 (×2) | ❌ missing | medium |  |
| Export All Holdings CSV | CLAUDE.md Features | ❌ missing | medium |  |
| Print / Export Report Mode | cli-prompts/print-export-patch.md | ❌ missing | medium |  |
| `emailBtn` (id) | 6790f467-65e5-4043-923d-14cd2da4c529.jsonl:L1341, 6790f467-65e5-4043-923d-14cd2da4c529/subagents/agent-acompact-51ea98d896d5f5d7.jsonl:L203, bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompa… (×4) | ✅ present | medium |  |
| Copy Summary button | CLAUDE.md Features | ✅ present | medium |  |
| `emailPreviewBtn` (id) | fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L1115 | ❌ missing | low |  |
| `emailPreviewContent` (id) | fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L1101, fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L1105 (×2) | ❌ missing | low |  |
| `emailPreviewFrame` (id) | fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L1141 | ❌ missing | low |  |

### factor

| Feature | Source(s) | Status | Priority | Notes |
|---|---|---|---|---|
| Factor Contributions (Risk inline) | TILE_SPEC.md Tier 2 #9 | 🤷 unclear | high |  |
| Factor Detail (cardFacDetail) | TILE_SPEC.md Tier 2 #8 | ✅ present | high |  |
| Factor Exposures Table (Risk inline) | TILE_SPEC.md Tier 2 #12 | 🤷 unclear | high |  |
| Factor Risk Budget (cardFRB) | TILE_SPEC.md Tier 2 #11 | ✅ present | high |  |
| `facDrillHoldBarDiv` (id) | bf250eb0-8cb6-4c32-96f7-d26d443c8a97.jsonl:L457, bf250eb0-8cb6-4c32-96f7-d26d443c8a97.jsonl:L464, bf250eb0-8cb6-4c32-96f7-d26d443c8a97.jsonl:L471 (×3) | ❌ missing | medium |  |
| `facSecBody` (id) | 875a1df5-d045-4fed-bd15-774cf1ce2337.jsonl:L152, 875a1df5-d045-4fed-bd15-774cf1ce2337/subagents/agent-acompact-36cc92af1a191d24.jsonl:L140, 9bb62f73-0e91-4b88-8263-95e8523b2238.jsonl:L742 (×4) | ❌ missing (regressed) | medium |  |
| `facSecLabel` (id) | 875a1df5-d045-4fed-bd15-774cf1ce2337.jsonl:L152, 875a1df5-d045-4fed-bd15-774cf1ce2337/subagents/agent-acompact-36cc92af1a191d24.jsonl:L140, 9bb62f73-0e91-4b88-8263-95e8523b2238.jsonl:L742 (×4) | ❌ missing (regressed) | medium |  |
| `facSecToggleRow` (id) | 875a1df5-d045-4fed-bd15-774cf1ce2337.jsonl:L152, 875a1df5-d045-4fed-bd15-774cf1ce2337/subagents/agent-acompact-36cc92af1a191d24.jsonl:L140, 9bb62f73-0e91-4b88-8263-95e8523b2238.jsonl:L742 (×4) | ❌ missing (regressed) | medium |  |
| `toggleFacSecondary` (onclick) | 875a1df5-d045-4fed-bd15-774cf1ce2337.jsonl:L152, 875a1df5-d045-4fed-bd15-774cf1ce2337/subagents/agent-acompact-36cc92af1a191d24.jsonl:L140, 9bb62f73-0e91-4b88-8263-95e8523b2238.jsonl:L742 (×4) | ❌ missing (regressed) | medium |  |
| `corrFactorSel` (id) | 0f6b5a8f-d645-4fb2-8123-64f4d239f8ce.jsonl:L128, 0f6b5a8f-d645-4fb2-8123-64f4d239f8ce/subagents/agent-acompact-840fe4766c4084ee.jsonl:L97, b2861e29-fdab-4386-a79d-886c89059725.jsonl:L644 (×9) | ✅ present (new) | medium |  |
| `facDrillHistDiv` (id) | 875a1df5-d045-4fed-bd15-774cf1ce2337.jsonl:L236, ba86eb57-dba7-45dc-b413-19e7cbec2c99.jsonl:L249, bf250eb0-8cb6-4c32-96f7-d26d443c8a97.jsonl:L457 (×6) | ✅ present | medium |  |
| `facDrillRetDiv` (id) | 875a1df5-d045-4fed-bd15-774cf1ce2337.jsonl:L236, bf250eb0-8cb6-4c32-96f7-d26d443c8a97.jsonl:L457, bf250eb0-8cb6-4c32-96f7-d26d443c8a97.jsonl:L464 (×5) | ✅ present | medium |  |
| `oDrFacRiskBreak` (onclick) | 0b5f4d42-6701-4c91-b48c-1175ffd26efa/subagents/agent-a5ac9021ea6323712.jsonl:L94, 0b5f4d42-6701-4c91-b48c-1175ffd26efa/subagents/agent-a5ac9021ea6323712.jsonl:L97, 0f6b5a8f-d645-4fb2-8123-64f4d239f8ce… (×15) | ✅ present (new) | medium |  |
| `rFac` (function) | 875a1df5-d045-4fed-bd15-774cf1ce2337.jsonl:L152, 875a1df5-d045-4fed-bd15-774cf1ce2337/subagents/agent-acompact-36cc92af1a191d24.jsonl:L140, bf250eb0-8cb6-4c32-96f7-d26d443c8a97.jsonl:L699 (×5) | ✅ present | medium |  |
| `rFacButt` (function) | bf250eb0-8cb6-4c32-96f7-d26d443c8a97.jsonl:L677, bf250eb0-8cb6-4c32-96f7-d26d443c8a97.jsonl:L686, bf250eb0-8cb6-4c32-96f7-d26d443c8a97/subagents/agent-ad34f454afdb0c094.jsonl:L85 (×4) | ✅ present | medium |  |
| `rFacWaterfall` (function) | 0306b5a0-0173-4ce1-8e03-64e3cca07936.jsonl:L655, b2861e29-fdab-4386-a79d-886c89059725.jsonl:L215, b2861e29-fdab-4386-a79d-886c89059725/subagents/agent-acompact-7d364f7476edf88e.jsonl:L71 (×5) | ✅ present (new) | medium |  |
| `updateFacExpChart` (function) | b2861e29-fdab-4386-a79d-886c89059725.jsonl:L133, b2861e29-fdab-4386-a79d-886c89059725.jsonl:L394, b2861e29-fdab-4386-a79d-886c89059725.jsonl:L657 (×8) | ✅ present (new) | medium |  |
| Factor Butterfly (cardFacButt) | TILE_SPEC.md Tier 5 #21 | ✅ present | medium |  |
| Factor Exposure History (Risk) | TILE_SPEC.md Tier 5 #27 | 🤷 unclear | medium |  |
| `facDrillDualDiv` (id) | fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L2216 | ❌ missing | low |  |
| `facGrpName` (function) | bf250eb0-8cb6-4c32-96f7-d26d443c8a97.jsonl:L686 | ❌ missing | low |  |
| `facQuad_BL` (id) | bf250eb0-8cb6-4c32-96f7-d26d443c8a97/subagents/agent-ad34f454afdb0c094.jsonl:L104 | ❌ missing | low |  |
| `facQuad_BR` (id) | bf250eb0-8cb6-4c32-96f7-d26d443c8a97/subagents/agent-ad34f454afdb0c094.jsonl:L104 | ❌ missing | low |  |
| `facQuad_TL` (id) | bf250eb0-8cb6-4c32-96f7-d26d443c8a97/subagents/agent-ad34f454afdb0c094.jsonl:L104 | ❌ missing | low |  |
| `facQuad_TR` (id) | bf250eb0-8cb6-4c32-96f7-d26d443c8a97/subagents/agent-ad34f454afdb0c094.jsonl:L104 | ❌ missing | low |  |
| `facRow` (function) | 875a1df5-d045-4fed-bd15-774cf1ce2337.jsonl:L152, 875a1df5-d045-4fed-bd15-774cf1ce2337/subagents/agent-acompact-36cc92af1a191d24.jsonl:L140 (×2) | ❌ missing (regressed) | low |  |
| `facTEWaterfallDiv` (id) | fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L2132 | ❌ missing | low |  |
| `hfcCell` (function) | bf250eb0-8cb6-4c32-96f7-d26d443c8a97.jsonl:L570 | ❌ missing | low |  |
| `hfpCell` (function) | fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L459 | ❌ missing | low |  |
| `rFacSubGroups` (function) | bf250eb0-8cb6-4c32-96f7-d26d443c8a97.jsonl:L696, bf250eb0-8cb6-4c32-96f7-d26d443c8a97.jsonl:L833 (×2) | ❌ missing | low |  |
| `rFacTEWaterfall` (function) | fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L2141 | ❌ missing | low |  |
| `setFacButtActiveOnly` (function) | bf250eb0-8cb6-4c32-96f7-d26d443c8a97/subagents/agent-ad34f454afdb0c094.jsonl:L85 | ❌ missing | low |  |
| `setFacButtQuad` (function) | bf250eb0-8cb6-4c32-96f7-d26d443c8a97/subagents/agent-ad34f454afdb0c094.jsonl:L85 | ❌ missing | low |  |
| `setFacButtQuad` (onclick) | bf250eb0-8cb6-4c32-96f7-d26d443c8a97/subagents/agent-ad34f454afdb0c094.jsonl:L104 | ❌ missing | low |  |
| `setFacGrp` (function) | 0f6b5a8f-d645-4fb2-8123-64f4d239f8ce.jsonl:L184 | ❌ missing | low |  |
| `setFacGrp` (onclick) | 0f6b5a8f-d645-4fb2-8123-64f4d239f8ce.jsonl:L128, 0f6b5a8f-d645-4fb2-8123-64f4d239f8ce/subagents/agent-acompact-840fe4766c4084ee.jsonl:L97 (×2) | ❌ missing | low |  |
| `thrFacExpMax` (id) | 0306b5a0-0173-4ce1-8e03-64e3cca07936.jsonl:L2441 | ❌ missing | low |  |
| `toggleFacSecondary` (function) | 875a1df5-d045-4fed-bd15-774cf1ce2337.jsonl:L156, 875a1df5-d045-4fed-bd15-774cf1ce2337/subagents/agent-acompact-36cc92af1a191d24.jsonl:L143 (×2) | ❌ missing (regressed) | low |  |
| `toggleFacSub` (function) | bf250eb0-8cb6-4c32-96f7-d26d443c8a97.jsonl:L696 | ❌ missing | low |  |
| `toggleFacSub` (onclick) | bf250eb0-8cb6-4c32-96f7-d26d443c8a97.jsonl:L696, bf250eb0-8cb6-4c32-96f7-d26d443c8a97.jsonl:L833 (×2) | ❌ missing | low |  |
| `cardFacButt` (id) | bf250eb0-8cb6-4c32-96f7-d26d443c8a97/subagents/agent-ad34f454afdb0c094.jsonl:L104, bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompact-2b2e69850cfd4eef.jsonl:L182, fbae49d0-369a-42ae-8bee-3f… (×3) | ✅ present | low |  |
| `facButtDiv` (id) | bf250eb0-8cb6-4c32-96f7-d26d443c8a97.jsonl:L2494, bf250eb0-8cb6-4c32-96f7-d26d443c8a97/subagents/agent-ad34f454afdb0c094.jsonl:L104, bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompact-2b2e6… (×4) | ✅ present | low |  |
| `facGrpColor` (function) | bf250eb0-8cb6-4c32-96f7-d26d443c8a97.jsonl:L686, fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L2929 (×2) | ✅ present (new) | low |  |
| `oDrFacRiskBreak` (function) | b2861e29-fdab-4386-a79d-886c89059725.jsonl:L359, b2861e29-fdab-4386-a79d-886c89059725/subagents/agent-acompact-7d364f7476edf88e.jsonl:L200 (×2) | ✅ present (new) | low |  |
| `rFacTopTeStrip` (function) | fbae49d0-369a-42ae-8bee-3fbd440690f7.jsonl:L190 | ✅ present (new) | low |  |

### group-rwd

| Feature | Source(s) | Status | Priority | Notes |
|---|---|---|---|---|
| Redwood Groups (cardGroups) | TILE_SPEC.md Tier 3 #15 | ✅ present | medium |  |
| `grpAvg` (function) | fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L725 | ❌ missing | low |  |
| `grpChartActive` (id) | fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L748 | ❌ missing | low |  |
| `grpChartBfly` (id) | fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L748 | ❌ missing | low |  |
| `grpDrillBarDiv` (id) | fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L841 | ❌ missing | low |  |
| `grpRankAvg` (id) | fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L725 | ❌ missing | low |  |
| `grpRankBM` (id) | fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L725 | ❌ missing | low |  |
| `grpRankPort` (id) | fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L725 | ❌ missing | low |  |
| `grpRankWtd` (id) | fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L725 | ❌ missing | low |  |
| `rGrpChartActive` (function) | fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L759 | ❌ missing | low |  |
| `setGrpRankMode` (function) | fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L722 | ❌ missing | low |  |
| `setGrpRankSrc` (function) | bf250eb0-8cb6-4c32-96f7-d26d443c8a97.jsonl:L1188, fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L722 (×2) | ❌ missing | low |  |
| `switchGrpChart` (function) | fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L759 | ❌ missing | low |  |
| `switchGrpChart` (onclick) | fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L748 | ❌ missing | low |  |
| `grpChart` (id) | bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompact-2b2e69850cfd4eef.jsonl:L182, fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L748 (×2) | ✅ present | low |  |
| `grpChartDiv` (id) | bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompact-2b2e69850cfd4eef.jsonl:L182, fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L748 (×2) | ✅ present | low |  |

### holdings-cards

| Feature | Source(s) | Status | Priority | Notes |
|---|---|---|---|---|
| `fillHoldCardsChunked` (function) | fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L595, fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L599, fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L610 (×6) | ❌ missing | high |  |
| `renderHoldCards` (function) | fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L595, fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L599, fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L610 (×9) | ❌ missing | high |  |
| `setHoldChip` (function) | 0306b5a0-0173-4ce1-8e03-64e3cca07936.jsonl:L1706, 0306b5a0-0173-4ce1-8e03-64e3cca07936.jsonl:L1712, 0306b5a0-0173-4ce1-8e03-64e3cca07936.jsonl:L1724 (×5) | ❌ missing | high |  |
| `toggleHoldExpand` (function) | fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L1537, fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L1651, fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L2024 (×6) | ❌ missing | high |  |
| `toggleHoldExpand` (onclick) | 0306b5a0-0173-4ce1-8e03-64e3cca07936.jsonl:L728, 0306b5a0-0173-4ce1-8e03-64e3cca07936.jsonl:L804, fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L115 (×7) | ❌ missing | high |  |
| `applyHoldSort` (function) | 0306b5a0-0173-4ce1-8e03-64e3cca07936.jsonl:L787, e62cfdfe-d20a-4c51-b748-89a29ac13385.jsonl:L22, fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L656 (×5) | ✅ present (new) | high |  |
| `renderHoldRows` (function) | 0306b5a0-0173-4ce1-8e03-64e3cca07936.jsonl:L804, 875a1df5-d045-4fed-bd15-774cf1ce2337.jsonl:L174, 875a1df5-d045-4fed-bd15-774cf1ce2337/subagents/agent-acompact-36cc92af1a191d24.jsonl:L156 (×6) | ✅ present | high |  |
| `renderHoldTab` (function) | 0f6b5a8f-d645-4fb2-8123-64f4d239f8ce.jsonl:L188, 0f6b5a8f-d645-4fb2-8123-64f4d239f8ce.jsonl:L196, 875a1df5-d045-4fed-bd15-774cf1ce2337.jsonl:L174 (×5) | ✅ present | high |  |
| `setHoldSort` (onclick) | 0306b5a0-0173-4ce1-8e03-64e3cca07936.jsonl:L1751, 0306b5a0-0173-4ce1-8e03-64e3cca07936.jsonl:L790, e62cfdfe-d20a-4c51-b748-89a29ac13385.jsonl:L31 (×7) | ✅ present (new) | high |  |
| `holdSummaryBar` (function) | fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L115, holdings-tab-spec.md:L58, holdings-tab-spec.md:L68 (×3) | ❌ missing | medium |  |
| `holdTbody` (id) | bf250eb0-8cb6-4c32-96f7-d26d443c8a97.jsonl:L910, bf250eb0-8cb6-4c32-96f7-d26d443c8a97.jsonl:L918, bf250eb0-8cb6-4c32-96f7-d26d443c8a97.jsonl:L925 (×5) | ❌ missing | medium |  |
| `setHoldChip` (onclick) | fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L1204, fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L1216, fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L587 (×3) | ❌ missing | medium |  |
| `setHoldView` (function) | fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L1360, fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L491, holdings-tab-spec.md:L68 (×3) | ❌ missing | medium |  |
| `setHoldSort` (function) | 0306b5a0-0173-4ce1-8e03-64e3cca07936.jsonl:L787, e62cfdfe-d20a-4c51-b748-89a29ac13385.jsonl:L22, fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L1365 (×4) | ✅ present (new) | medium |  |
| `copyBuilderSummary` (function) | fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L465 | ❌ missing | low |  |
| `copyBuilderSummary` (onclick) | fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L486 | ❌ missing | low |  |
| `fillHoldTbodyChunked` (function) | fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L115 | ❌ missing | low |  |
| `hideHoldHover` (function) | 0306b5a0-0173-4ce1-8e03-64e3cca07936.jsonl:L725 | ❌ missing | low |  |
| `holdCardGrid` (id) | fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L659, fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L955 (×2) | ❌ missing | low |  |
| `holdHoverPop` (id) | 0306b5a0-0173-4ce1-8e03-64e3cca07936.jsonl:L717 | ❌ missing | low |  |
| `holdRowCtxMenu` (function) | fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L2024 | ❌ missing | low |  |
| `holdRowCtxMenu` (onclick) | fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L2017 | ❌ missing | low |  |
| `holdSortCtrl` (id) | 0f6b5a8f-d645-4fb2-8123-64f4d239f8ce.jsonl:L188 | ❌ missing | low |  |
| `renderHold` (function) | 0306b5a0-0173-4ce1-8e03-64e3cca07936.jsonl:L804, fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L1383 (×2) | ❌ missing | low |  |
| `renderHoldExpandedRow` (function) | holdings-tab-spec.md:L58, holdings-tab-spec.md:L68 (×2) | ❌ missing | low |  |
| `renderHoldFacCharts` (function) | fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L1651 | ❌ missing | low |  |
| `saveHoldPrefs` (function) | 0306b5a0-0173-4ce1-8e03-64e3cca07936.jsonl:L1678, fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L1360 (×2) | ❌ missing | low |  |
| `setHoldGroupBy` (function) | fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L1362, fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L948 (×2) | ❌ missing | low |  |
| `setHoldGroupBy` (onclick) | fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L955 | ❌ missing | low |  |
| `setHoldView` (onclick) | holdings-tab-spec.md:L68 | ❌ missing | low |  |
| `showHoldHover` (function) | 0306b5a0-0173-4ce1-8e03-64e3cca07936.jsonl:L725, fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L1662 (×2) | ❌ missing | low |  |
| `sortHoldQuick` (function) | 0f6b5a8f-d645-4fb2-8123-64f4d239f8ce.jsonl:L196 | ❌ missing | low |  |
| `sortHoldQuick` (onclick) | 0f6b5a8f-d645-4fb2-8123-64f4d239f8ce.jsonl:L188 | ❌ missing | low |  |
| `toggleHoldSecFilter` (function) | 0306b5a0-0173-4ce1-8e03-64e3cca07936.jsonl:L1718, 0306b5a0-0173-4ce1-8e03-64e3cca07936.jsonl:L1724 (×2) | ❌ missing | low |  |
| `toggleHoldSecFilter` (onclick) | 0306b5a0-0173-4ce1-8e03-64e3cca07936.jsonl:L1744 | ❌ missing | low |  |
| `toggleHoldSelect` (function) | fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L465 | ❌ missing | low |  |

### holdings-general

| Feature | Source(s) | Status | Priority | Notes |
|---|---|---|---|---|
| `Sector Concentration (Top 10 Holdings)` (card-title) | 875a1df5-d045-4fed-bd15-774cf1ce2337.jsonl:L174, 875a1df5-d045-4fed-bd15-774cf1ce2337/subagents/agent-acompact-36cc92af1a191d24.jsonl:L156, holdings-tab-spec.md:L68 (×3) | ❌ missing (regressed) | high |  |
| `exportAllHoldings` (onclick) | 0f6b5a8f-d645-4fb2-8123-64f4d239f8ce.jsonl:L188, 6790f467-65e5-4043-923d-14cd2da4c529.jsonl:L1360, 6790f467-65e5-4043-923d-14cd2da4c529/subagents/agent-acompact-51ea98d896d5f5d7.jsonl:L217 (×7) | ✅ present | high |  |
| `Holdings Count` (card-title) | 33df0d54-3b91-47b9-8d9b-71ad1f12c0c9.jsonl:L126, b2861e29-fdab-4386-a79d-886c89059725.jsonl:L133, b2861e29-fdab-4386-a79d-886c89059725/subagents/agent-acompact-9d785f21d8fa6596.jsonl:L67 (×3) | ✅ present | high |  |
| `Holdings Overlap` (card-title) | 6790f467-65e5-4043-923d-14cd2da4c529.jsonl:L1384, 6790f467-65e5-4043-923d-14cd2da4c529/subagents/agent-acompact-51ea98d896d5f5d7.jsonl:L238, 9bb62f73-0e91-4b88-8263-95e8523b2238.jsonl:L1203 (×4) | ✅ present | high |  |
| Holdings Table (cardHoldings) | TILE_SPEC.md Tier 1 #5; tile-specs/holdings-tab-spec.md | ✅ present | high |  |
| `Holdings by Stock-Specific TE (%S) — sorted descending` (card-title) | 875a1df5-d045-4fed-bd15-774cf1ce2337.jsonl:L211 | ❌ missing (regressed) | medium |  |
| `Holdings-Level Decomposition` (card-title) | bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompact-2b2e69850cfd4eef.jsonl:L59 | ❌ missing (regressed) | medium |  |
| `Portfolio Holdings ('+(cs.sum.h\|\|'\u2014')+')` (card-title) | holdings-tab-spec.md:L68 | ❌ missing | medium |  |
| `Top Holdings by Factor Contribution (${facHolds.length})` (card-title) | bf250eb0-8cb6-4c32-96f7-d26d443c8a97.jsonl:L457, bf250eb0-8cb6-4c32-96f7-d26d443c8a97.jsonl:L464, bf250eb0-8cb6-4c32-96f7-d26d443c8a97.jsonl:L471 (×3) | ❌ missing | medium |  |
| Holdings Intelligence Layer | cli-prompts/holdings-intelligence-patch.md | ❌ missing | medium |  |
| `Avg Quant Scores — ${holdings.length} Holdings` (card-title) | 9bb62f73-0e91-4b88-8263-95e8523b2238.jsonl:L214, 9bb62f73-0e91-4b88-8263-95e8523b2238/subagents/agent-acompact-5d03aa71ce7b3960.jsonl:L212, 9bb62f73-0e91-4b88-8263-95e8523b2238/subagents/agent-aside_q… (×7) | ✅ present (new) | medium |  |
| `cardHoldings` (id) | 0306b5a0-0173-4ce1-8e03-64e3cca07936.jsonl:L1732, 0306b5a0-0173-4ce1-8e03-64e3cca07936.jsonl:L1737, 0f6b5a8f-d645-4fb2-8123-64f4d239f8ce.jsonl:L188 (×10) | ✅ present | medium |  |
| `exportAllHoldings` (function) | 6790f467-65e5-4043-923d-14cd2da4c529.jsonl:L1352, 6790f467-65e5-4043-923d-14cd2da4c529/subagents/agent-acompact-51ea98d896d5f5d7.jsonl:L211, fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L330 (×3) | ✅ present | medium |  |
| `Holdings in ${name} (${holdings.length})` (card-title) | bf250eb0-8cb6-4c32-96f7-d26d443c8a97.jsonl:L2465, bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompact-2b2e69850cfd4eef.jsonl:L103, bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompa… (×5) | ✅ present | medium |  |
| `Holdings` (card-title) | b7818bde-fbfd-4187-a4c0-2518a1e4cbd0.jsonl:L120 | ✅ present | medium |  |
| `Portfolio Holdings (${fh.length})` (card-title) | 0f6b5a8f-d645-4fb2-8123-64f4d239f8ce.jsonl:L188, 875a1df5-d045-4fed-bd15-774cf1ce2337.jsonl:L174, 875a1df5-d045-4fed-bd15-774cf1ce2337/subagents/agent-acompact-36cc92af1a191d24.jsonl:L156 (×4) | ✅ present | medium |  |
| `Shared Holdings (top 15 by ${keys[0]} weight)` (card-title) | 6790f467-65e5-4043-923d-14cd2da4c529.jsonl:L1384, 6790f467-65e5-4043-923d-14cd2da4c529/subagents/agent-acompact-51ea98d896d5f5d7.jsonl:L238, 9bb62f73-0e91-4b88-8263-95e8523b2238.jsonl:L1203 (×4) | ✅ present | medium |  |
| `tabHoldings` (id) | 0f6b5a8f-d645-4fb2-8123-64f4d239f8ce.jsonl:L64, 0f6b5a8f-d645-4fb2-8123-64f4d239f8ce/subagents/agent-acompact-840fe4766c4084ee.jsonl:L51, 6790f467-65e5-4043-923d-14cd2da4c529.jsonl:L1287 (×4) | ✅ present | medium |  |
| `Top 10 Holdings (Weight &amp; Active)` (card-title) | fbae49d0-369a-42ae-8bee-3fbd440690f7.jsonl:L113 | ✅ present (new) | medium |  |
| Rank Distribution (Holdings) | TILE_SPEC.md Tier 5 #28 | 🤷 unclear | medium |  |
| Sector Concentration Top 10 (Holdings) | TILE_SPEC.md Tier 5 #29 | 🤷 unclear | medium |  |
| `Holdings (${holdings.length}) — sorted by TE` (card-title) | fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L841 | ❌ missing | low |  |
| `oDrCompareHoldings` (function) | fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L2024 | ❌ missing | low |  |
| `oDrCompareHoldings` (onclick) | fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L2017 | ❌ missing | low |  |
| `Top Holdings by TE — ${groupName}` (card-title) | fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L841 | ❌ missing | low |  |
| `Top Holdings by TE — ${name} (${holdings.length} total)` (card-title) | bf250eb0-8cb6-4c32-96f7-d26d443c8a97.jsonl:L356 | ❌ missing | low |  |
| `Top Holdings by TE — ${name}` (card-title) | bf250eb0-8cb6-4c32-96f7-d26d443c8a97.jsonl:L2465, fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L838 (×2) | ❌ missing | low |  |
| `Holdings (${holdings.length})` (card-title) | 9bb62f73-0e91-4b88-8263-95e8523b2238.jsonl:L1621, bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompact-2b2e69850cfd4eef.jsonl:L59 (×2) | ✅ present | low |  |
| `tab-holdings` (id) | 0f6b5a8f-d645-4fb2-8123-64f4d239f8ce.jsonl:L68, 0f6b5a8f-d645-4fb2-8123-64f4d239f8ce/subagents/agent-acompact-840fe4766c4084ee.jsonl:L54 (×2) | ✅ present | low |  |
| `Your Holdings in ${u.reg} (${secHold.length})` (card-title) | bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompact-2b2e69850cfd4eef.jsonl:L59 | ✅ present | low |  |

### mini-charts

| Feature | Source(s) | Status | Priority | Notes |
|---|---|---|---|---|
| Historical Trends mini-charts (TE, AS, Beta, Holdings) | CLAUDE.md Features | ❌ missing | high |  |
| rHistoricalTrends mini-charts | GAP_DISCOVERY.md example; CLAUDE.md | ❌ missing | high |  |
| Summary Card — Factor Risk | TILE_SPEC.md Tier 1 #3 | ❌ missing | high |  |
| Summary Card — Idiosyncratic Risk | TILE_SPEC.md Tier 1 #2 | ✅ present | high |  |
| Summary Card — Tracking Error | TILE_SPEC.md Tier 1 #1 | ✅ present | high | Exposures top-row inline sum-card; click → oDrMetric(te) |
| `miniH` (id) | 33df0d54-3b91-47b9-8d9b-71ad1f12c0c9.jsonl:L126, 6790f467-65e5-4043-923d-14cd2da4c529.jsonl:L1416, 6790f467-65e5-4043-923d-14cd2da4c529/subagents/agent-acompact-51ea98d896d5f5d7.jsonl:L265 (×5) | ❌ missing (regressed) | medium |  |
| `miniAS` (id) | 6790f467-65e5-4043-923d-14cd2da4c529.jsonl:L1416, 6790f467-65e5-4043-923d-14cd2da4c529/subagents/agent-acompact-51ea98d896d5f5d7.jsonl:L265 (×2) | ❌ missing | low |  |
| `miniTE` (id) | 6790f467-65e5-4043-923d-14cd2da4c529.jsonl:L1416, 6790f467-65e5-4043-923d-14cd2da4c529/subagents/agent-acompact-51ea98d896d5f5d7.jsonl:L265 (×2) | ❌ missing | low |  |

### misc

| Feature | Source(s) | Status | Priority | Notes |
|---|---|---|---|---|
| Historical week banner (amber) for past weeks | CLAUDE.md Features | ❌ missing | high |  |
| `Active Exposure` (card-title) | 875a1df5-d045-4fed-bd15-774cf1ce2337.jsonl:L236, 875a1df5-d045-4fed-bd15-774cf1ce2337.jsonl:L259, bf250eb0-8cb6-4c32-96f7-d26d443c8a97.jsonl:L457 (×6) | ✅ present | high |  |
| `Active Weight Treemap` (card-title) | active-weight-treemap-spec.md:L103, active-weight-treemap-spec.md:L95, bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompact-2b2e69850cfd4eef.jsonl:L182 (×3) | ✅ present | high |  |
| `Factor Contributions` (card-title) | 0f6b5a8f-d645-4fb2-8123-64f4d239f8ce.jsonl:L128, 0f6b5a8f-d645-4fb2-8123-64f4d239f8ce/subagents/agent-acompact-840fe4766c4084ee.jsonl:L97, b2861e29-fdab-4386-a79d-886c89059725.jsonl:L376 (×8) | ✅ present (new) | high |  |
| `Factor Correlation Matrix` (card-title) | 0f6b5a8f-d645-4fb2-8123-64f4d239f8ce.jsonl:L128, 0f6b5a8f-d645-4fb2-8123-64f4d239f8ce/subagents/agent-acompact-840fe4766c4084ee.jsonl:L97, 33df0d54-3b91-47b9-8d9b-71ad1f12c0c9.jsonl:L126 (×17) | ✅ present | high |  |
| `Factor Detail` (card-title) | 0306b5a0-0173-4ce1-8e03-64e3cca07936.jsonl:L866, 0306b5a0-0173-4ce1-8e03-64e3cca07936.jsonl:L870, bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompact-2b2e69850cfd4eef.jsonl:L182 (×4) | ✅ present | high |  |
| `Factor Exposure History` (card-title) | 0f6b5a8f-d645-4fb2-8123-64f4d239f8ce.jsonl:L128, 0f6b5a8f-d645-4fb2-8123-64f4d239f8ce/subagents/agent-acompact-840fe4766c4084ee.jsonl:L97, b2861e29-fdab-4386-a79d-886c89059725.jsonl:L133 (×4) | ✅ present | high |  |
| `Factor Return &amp; Impact` (card-title) | 875a1df5-d045-4fed-bd15-774cf1ce2337.jsonl:L236, 875a1df5-d045-4fed-bd15-774cf1ce2337.jsonl:L259, bf250eb0-8cb6-4c32-96f7-d26d443c8a97.jsonl:L457 (×6) | ✅ present | high |  |
| `Factor Risk Map` (card-title) | 0306b5a0-0173-4ce1-8e03-64e3cca07936.jsonl:L546, bf250eb0-8cb6-4c32-96f7-d26d443c8a97/subagents/agent-ad34f454afdb0c094.jsonl:L104, fbae49d0-369a-42ae-8bee-3fbd440690f7.jsonl:L187 (×3) | ✅ present (new) | high |  |
| `Historical Weight: Portfolio vs Benchmark` (card-title) | 9bb62f73-0e91-4b88-8263-95e8523b2238.jsonl:L1404, b2861e29-fdab-4386-a79d-886c89059725.jsonl:L229, b2861e29-fdab-4386-a79d-886c89059725/subagents/agent-acompact-7d364f7476edf88e.jsonl:L85 (×5) | ✅ present | high |  |
| `Region Active Weights` (card-title) | 0f6b5a8f-d645-4fb2-8123-64f4d239f8ce.jsonl:L128, 0f6b5a8f-d645-4fb2-8123-64f4d239f8ce/subagents/agent-acompact-840fe4766c4084ee.jsonl:L97, 875a1df5-d045-4fed-bd15-774cf1ce2337.jsonl:L145 (×6) | ✅ present | high |  |
| `rHold` (function) | 0306b5a0-0173-4ce1-8e03-64e3cca07936.jsonl:L1697, 875a1df5-d045-4fed-bd15-774cf1ce2337.jsonl:L164, 875a1df5-d045-4fed-bd15-774cf1ce2337/subagents/agent-acompact-36cc92af1a191d24.jsonl:L149 (×8) | ✅ present | high |  |
| `sortHold` (onclick) | 0306b5a0-0173-4ce1-8e03-64e3cca07936.jsonl:L725, 0f6b5a8f-d645-4fb2-8123-64f4d239f8ce.jsonl:L188, 6790f467-65e5-4043-923d-14cd2da4c529.jsonl:L862 (×14) | ✅ present | high |  |
| `Summary Statistics` (card-title) | 6790f467-65e5-4043-923d-14cd2da4c529.jsonl:L1384, 6790f467-65e5-4043-923d-14cd2da4c529/subagents/agent-acompact-51ea98d896d5f5d7.jsonl:L238, 875a1df5-d045-4fed-bd15-774cf1ce2337.jsonl:L306 (×6) | ✅ present | high |  |
| `Tracking Error — Factor vs Stock-Specific Decomposition` (card-title) | b2861e29-fdab-4386-a79d-886c89059725.jsonl:L133, b2861e29-fdab-4386-a79d-886c89059725/subagents/agent-acompact-9d785f21d8fa6596.jsonl:L67, bf250eb0-8cb6-4c32-96f7-d26d443c8a97.jsonl:L777 (×3) | ✅ present (new) | high |  |
| Historical Week Navigation Enhancement | cli-prompts/week-navigation-patch.md | 🤷 unclear | high |  |
| Portfolio Characteristics (cardChars) | TILE_SPEC.md Tier 1 #4; tile-specs/portfolio-characteristics-spec.md | ✅ present | high |  |
| `All Countries` (card-title) | bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompact-2b2e69850cfd4eef.jsonl:L182 | ❌ missing (regressed) | medium |  |
| `Contribution Outliers` (card-title) | bf250eb0-8cb6-4c32-96f7-d26d443c8a97.jsonl:L457, bf250eb0-8cb6-4c32-96f7-d26d443c8a97.jsonl:L464, bf250eb0-8cb6-4c32-96f7-d26d443c8a97.jsonl:L471 (×3) | ❌ missing | medium |  |
| `Factor Butterfly` (card-title) | bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompact-2b2e69850cfd4eef.jsonl:L182 | ❌ missing (regressed) | medium |  |
| `Factor Contribution to Risk` (card-title) | 6790f467-65e5-4043-923d-14cd2da4c529.jsonl:L1416, 6790f467-65e5-4043-923d-14cd2da4c529/subagents/agent-acompact-51ea98d896d5f5d7.jsonl:L265 (×2) | ❌ missing | medium |  |
| `Factor Contribution to Tracking Error` (card-title) | b2861e29-fdab-4386-a79d-886c89059725.jsonl:L133, b2861e29-fdab-4386-a79d-886c89059725/subagents/agent-acompact-9d785f21d8fa6596.jsonl:L67 (×2) | ❌ missing | medium |  |
| `Factor Contributions to Group TE` (card-title) | fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L841 | ❌ missing | medium |  |
| `Factor Exposure History (Active = Portfolio − Benchmark)` (card-title) | 33df0d54-3b91-47b9-8d9b-71ad1f12c0c9.jsonl:L126 | ❌ missing (regressed) | medium |  |
| `Factor Exposure vs Portfolio TE` (card-title) | fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L2216 | ❌ missing | medium |  |
| `Factor Exposures (${keys.slice(0,2).join(' vs ')})` (card-title) | 6790f467-65e5-4043-923d-14cd2da4c529.jsonl:L1384, 6790f467-65e5-4043-923d-14cd2da4c529/subagents/agent-acompact-51ea98d896d5f5d7.jsonl:L238 (×2) | ❌ missing (regressed) | medium |  |
| `Factor Profile` (card-title) | bf250eb0-8cb6-4c32-96f7-d26d443c8a97.jsonl:L606 | ❌ missing | medium |  |
| `Factor Risk Contribution (% of TE) — click bar for drill-down` (card-title) | 33df0d54-3b91-47b9-8d9b-71ad1f12c0c9.jsonl:L126 | ❌ missing (regressed) | medium |  |
| `Historical Trends` (card-title) | 6790f467-65e5-4043-923d-14cd2da4c529.jsonl:L1416, 6790f467-65e5-4043-923d-14cd2da4c529/subagents/agent-acompact-51ea98d896d5f5d7.jsonl:L265 (×2) | ❌ missing | medium |  |
| `holdColDropHtml` (function) | holdings-tab-spec.md:L48, holdings-tab-spec.md:L58, holdings-tab-spec.md:L68 (×3) | ❌ missing | medium |  |
| `Marginal Contribution to Risk (Top 10)` (card-title) | bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompact-2b2e69850cfd4eef.jsonl:L111, bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompact-2b2e69850cfd4eef.jsonl:L182 (×2) | ❌ missing (regressed) | medium |  |
| `oDrAllFactorRisk` (function) | 33df0d54-3b91-47b9-8d9b-71ad1f12c0c9.jsonl:L108, 33df0d54-3b91-47b9-8d9b-71ad1f12c0c9.jsonl:L185 (×2) | ❌ missing (regressed) | medium |  |
| `oDrAllFactorRisk` (onclick) | 33df0d54-3b91-47b9-8d9b-71ad1f12c0c9.jsonl:L103 | ❌ missing (regressed) | medium |  |
| `renderOneCard` (function) | fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L595, fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L599, fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L610 (×6) | ❌ missing | medium |  |
| `Similar Factor Profile` (card-title) | fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L966 | ❌ missing | medium |  |
| `toggleHoldCol` (function) | holdings-tab-spec.md:L48, holdings-tab-spec.md:L58, holdings-tab-spec.md:L68 (×3) | ❌ missing | medium |  |
| `Tracking Error — Idiosyncratic vs Factor Decomposition` (card-title) | 0f6b5a8f-d645-4fb2-8123-64f4d239f8ce.jsonl:L128, 0f6b5a8f-d645-4fb2-8123-64f4d239f8ce/subagents/agent-acompact-840fe4766c4084ee.jsonl:L97 (×2) | ❌ missing | medium |  |
| `Tracking Error — Stock-Specific (Gold) vs Factor Risk (Blue)` (card-title) | 33df0d54-3b91-47b9-8d9b-71ad1f12c0c9.jsonl:L126 | ❌ missing (regressed) | medium |  |
| `Weight History (synthetic)` (card-title) | 9bb62f73-0e91-4b88-8263-95e8523b2238.jsonl:L875, 9bb62f73-0e91-4b88-8263-95e8523b2238/subagents/agent-acompact-f59e4390ac8d39a6.jsonl:L228 (×2) | ❌ missing | medium |  |
| Currency Exposure Tile | cli-prompts/currency-exposure-tile-patch.md | ❌ missing | medium |  |
| Data Freshness + Auto-Reload + Upload History | cli-prompts/data-freshness-patch.md | ❌ missing | medium |  |
| Executive Summary Card (Weekly Insights) | cli-prompts/exec-summary-patch.md | ❌ missing | medium |  |
| Industry Deep Drill Enhancement | cli-prompts/industry-drilldown-patch.md | ❌ missing | medium |  |
| Layout Rearrangement + Full-Screen Chart Modals | cli-prompts/layout-and-fullscreen-patch.md | ❌ missing | medium |  |
| Onboarding + Contextual Help | cli-prompts/onboarding-tooltips-patch.md | ❌ missing | medium |  |
| Performance Optimization | cli-prompts/performance-optimization-patch.md | ❌ missing | medium |  |
| Quick-Nav Floating Sidebar | cli-prompts/quicknav-patch.md | ❌ missing | medium |  |
| Range buttons (3M\|6M\|1Y\|3Y\|All) on all drill charts | CLAUDE.md Features | ❌ missing (regressed) | medium |  |
| Scenario Analysis / What-If Engine | cli-prompts/scenario-analysis-patch.md | ❌ missing | medium |  |
| spotlightRanksToggle (W / Avg / BM) | GAP_DISCOVERY.md example; tile-specs/sector-active-weights-spec.md; user mention | ❌ missing | medium |  |
| Tab count badges (Holdings: equity count, Attribution: factor count) | CLAUDE.md Features | ❌ missing | medium |  |
| Week selector in header (‹ date ›) | CLAUDE.md Features | ❌ missing | medium |  |
| `Breakdown` (card-title) | bf250eb0-8cb6-4c32-96f7-d26d443c8a97.jsonl:L1652, bf250eb0-8cb6-4c32-96f7-d26d443c8a97.jsonl:L1656, bf250eb0-8cb6-4c32-96f7-d26d443c8a97.jsonl:L1660 (×4) | ✅ present | medium |  |
| `cardTreemap` (id) | active-weight-treemap-spec.md:L103, active-weight-treemap-spec.md:L95, bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompact-2b2e69850cfd4eef.jsonl:L182 (×3) | ✅ present | medium |  |
| `changeWeek` (function) | 0b5f4d42-6701-4c91-b48c-1175ffd26efa.jsonl:L227, 0b5f4d42-6701-4c91-b48c-1175ffd26efa/subagents/agent-acompact-df09ce4707361d21.jsonl:L225, ba86eb57-dba7-45dc-b413-19e7cbec2c99.jsonl:L157 (×4) | ✅ present | medium |  |
| `closeDrill` (onclick) | 33df0d54-3b91-47b9-8d9b-71ad1f12c0c9.jsonl:L108, 9bb62f73-0e91-4b88-8263-95e8523b2238.jsonl:L759, 9bb62f73-0e91-4b88-8263-95e8523b2238/subagents/agent-acompact-f59e4390ac8d39a6.jsonl:L113 (×11) | ✅ present | medium |  |
| `compFacDiv` (id) | 6790f467-65e5-4043-923d-14cd2da4c529.jsonl:L1384, 6790f467-65e5-4043-923d-14cd2da4c529/subagents/agent-acompact-51ea98d896d5f5d7.jsonl:L238, 9bb62f73-0e91-4b88-8263-95e8523b2238.jsonl:L1203 (×5) | ✅ present | medium |  |
| `copySummary` (function) | 6790f467-65e5-4043-923d-14cd2da4c529.jsonl:L1352, 6790f467-65e5-4043-923d-14cd2da4c529/subagents/agent-acompact-51ea98d896d5f5d7.jsonl:L211, fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L2929 (×3) | ✅ present | medium |  |
| `corrFreq` (id) | 0b5f4d42-6701-4c91-b48c-1175ffd26efa/subagents/agent-a619a31322509e7ca.jsonl:L130, 0f6b5a8f-d645-4fb2-8123-64f4d239f8ce.jsonl:L128, 0f6b5a8f-d645-4fb2-8123-64f4d239f8ce/subagents/agent-acompact-840fe4… (×13) | ✅ present (new) | medium |  |
| `corrPeriod` (id) | 0b5f4d42-6701-4c91-b48c-1175ffd26efa/subagents/agent-a619a31322509e7ca.jsonl:L127, 0f6b5a8f-d645-4fb2-8123-64f4d239f8ce.jsonl:L128, 0f6b5a8f-d645-4fb2-8123-64f4d239f8ce/subagents/agent-acompact-840fe4… (×10) | ✅ present (new) | medium |  |
| `cycleFlag` (onclick) | fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L2567, fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L2573, fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L2622 (×4) | ✅ present (new) | medium |  |
| `exportCSV` (onclick) | 0306b5a0-0173-4ce1-8e03-64e3cca07936.jsonl:L866, 0306b5a0-0173-4ce1-8e03-64e3cca07936.jsonl:L870, 875a1df5-d045-4fed-bd15-774cf1ce2337.jsonl:L145 (×13) | ✅ present | medium |  |
| `Exposure Time Series` (card-title) | bf250eb0-8cb6-4c32-96f7-d26d443c8a97.jsonl:L457, bf250eb0-8cb6-4c32-96f7-d26d443c8a97.jsonl:L464, bf250eb0-8cb6-4c32-96f7-d26d443c8a97.jsonl:L471 (×4) | ✅ present | medium |  |
| `facBarToggles` (id) | 0f6b5a8f-d645-4fb2-8123-64f4d239f8ce.jsonl:L128, 0f6b5a8f-d645-4fb2-8123-64f4d239f8ce/subagents/agent-acompact-840fe4766c4084ee.jsonl:L97, 9bb62f73-0e91-4b88-8263-95e8523b2238.jsonl:L879 (×8) | ✅ present (new) | medium |  |
| `Factor Active Exposures` (card-title) | 9bb62f73-0e91-4b88-8263-95e8523b2238.jsonl:L1203, 9bb62f73-0e91-4b88-8263-95e8523b2238/subagents/agent-acompact-278d4915e57367f7.jsonl:L255 (×2) | ✅ present (new) | medium |  |
| `Factor Exposures — click row for time series drill` (card-title) | b2861e29-fdab-4386-a79d-886c89059725.jsonl:L133, b2861e29-fdab-4386-a79d-886c89059725/subagents/agent-acompact-9d785f21d8fa6596.jsonl:L67 (×2) | ✅ present (new) | medium |  |
| `Factor Risk Budget` (card-title) | bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompact-2b2e69850cfd4eef.jsonl:L111, bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompact-2b2e69850cfd4eef.jsonl:L182 (×2) | ✅ present | medium |  |
| `filterByRank` (onclick) | 0b5f4d42-6701-4c91-b48c-1175ffd26efa/subagents/agent-a5ac9021ea6323712.jsonl:L100, 0b5f4d42-6701-4c91-b48c-1175ffd26efa/subagents/agent-a619a31322509e7ca.jsonl:L143, 6790f467-65e5-4043-923d-14cd2da4c5… (×10) | ✅ present | medium |  |
| `generateShareURL` (onclick) | 6790f467-65e5-4043-923d-14cd2da4c529.jsonl:L1341, 6790f467-65e5-4043-923d-14cd2da4c529/subagents/agent-acompact-51ea98d896d5f5d7.jsonl:L203, bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompa… (×3) | ✅ present | medium |  |
| `holdConcDiv` (id) | 875a1df5-d045-4fed-bd15-774cf1ce2337.jsonl:L174, 875a1df5-d045-4fed-bd15-774cf1ce2337/subagents/agent-acompact-36cc92af1a191d24.jsonl:L156, fbae49d0-369a-42ae-8bee-3fbd440690f7.jsonl:L113 (×4) | ✅ present | medium |  |
| `initWeekSelector` (function) | 0b5f4d42-6701-4c91-b48c-1175ffd26efa.jsonl:L193, 0b5f4d42-6701-4c91-b48c-1175ffd26efa.jsonl:L221, 0b5f4d42-6701-4c91-b48c-1175ffd26efa/subagents/agent-acompact-df09ce4707361d21.jsonl:L191 (×6) | ✅ present | medium |  |
| `jumpToLatest` (function) | 0b5f4d42-6701-4c91-b48c-1175ffd26efa.jsonl:L227, 0b5f4d42-6701-4c91-b48c-1175ffd26efa/subagents/agent-acompact-df09ce4707361d21.jsonl:L225, ba86eb57-dba7-45dc-b413-19e7cbec2c99.jsonl:L157 (×4) | ✅ present | medium |  |
| `Key Metrics` (card-title) | 9bb62f73-0e91-4b88-8263-95e8523b2238.jsonl:L875, 9bb62f73-0e91-4b88-8263-95e8523b2238/subagents/agent-acompact-f59e4390ac8d39a6.jsonl:L228 (×2) | ✅ present (new) | medium |  |
| `oDr` (function) | 9bb62f73-0e91-4b88-8263-95e8523b2238.jsonl:L1004, 9bb62f73-0e91-4b88-8263-95e8523b2238/subagents/agent-acompact-278d4915e57367f7.jsonl:L57, bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompac… (×3) | ✅ present | medium |  |
| `oDr` (onclick) | 9bb62f73-0e91-4b88-8263-95e8523b2238.jsonl:L1008, 9bb62f73-0e91-4b88-8263-95e8523b2238/subagents/agent-acompact-278d4915e57367f7.jsonl:L61, bf250eb0-8cb6-4c32-96f7-d26d443c8a97.jsonl:L333 (×6) | ✅ present | medium |  |
| `oDrChar` (onclick) | 0306b5a0-0173-4ce1-8e03-64e3cca07936.jsonl:L1566, 0306b5a0-0173-4ce1-8e03-64e3cca07936.jsonl:L1570, 6790f467-65e5-4043-923d-14cd2da4c529.jsonl:L729 (×12) | ✅ present | medium |  |
| `oDrF` (function) | ba86eb57-dba7-45dc-b413-19e7cbec2c99.jsonl:L249, bf250eb0-8cb6-4c32-96f7-d26d443c8a97.jsonl:L457, bf250eb0-8cb6-4c32-96f7-d26d443c8a97.jsonl:L464 (×4) | ✅ present | medium |  |
| `oDrF` (onclick) | 0306b5a0-0173-4ce1-8e03-64e3cca07936.jsonl:L887, 0306b5a0-0173-4ce1-8e03-64e3cca07936.jsonl:L891, 0306b5a0-0173-4ce1-8e03-64e3cca07936.jsonl:L895 (×25) | ✅ present | medium |  |
| `oDrFRisk` (onclick) | 6790f467-65e5-4043-923d-14cd2da4c529.jsonl:L1002, 6790f467-65e5-4043-923d-14cd2da4c529.jsonl:L1437, 6790f467-65e5-4043-923d-14cd2da4c529/subagents/agent-acompact-31f87266afe462b7.jsonl:L250 (×10) | ✅ present | medium |  |
| `oDrGroup` (function) | 0b5f4d42-6701-4c91-b48c-1175ffd26efa.jsonl:L199, 0b5f4d42-6701-4c91-b48c-1175ffd26efa/subagents/agent-acompact-df09ce4707361d21.jsonl:L197, bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompac… (×4) | ✅ present | medium |  |
| `oDrGroup` (onclick) | 0b5f4d42-6701-4c91-b48c-1175ffd26efa.jsonl:L196, 0b5f4d42-6701-4c91-b48c-1175ffd26efa/subagents/agent-acompact-df09ce4707361d21.jsonl:L194, 9bb62f73-0e91-4b88-8263-95e8523b2238.jsonl:L755 (×6) | ✅ present | medium |  |
| `oDrMetric` (function) | 875a1df5-d045-4fed-bd15-774cf1ce2337.jsonl:L211, ba86eb57-dba7-45dc-b413-19e7cbec2c99.jsonl:L212, bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompact-2b2e69850cfd4eef.jsonl:L294 (×5) | ✅ present | medium |  |
| `oDrMetric` (onclick) | 0b5f4d42-6701-4c91-b48c-1175ffd26efa/subagents/agent-a5ac9021ea6323712.jsonl:L94, 0b5f4d42-6701-4c91-b48c-1175ffd26efa/subagents/agent-a5ac9021ea6323712.jsonl:L97, 0f6b5a8f-d645-4fb2-8123-64f4d239f8ce… (×39) | ✅ present | medium |  |
| `oDrUnowned` (onclick) | 9bb62f73-0e91-4b88-8263-95e8523b2238.jsonl:L1625, bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompact-2b2e69850cfd4eef.jsonl:L79, fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L1805 (×3) | ✅ present | medium |  |
| `openComp` (function) | 6790f467-65e5-4043-923d-14cd2da4c529.jsonl:L1380, 6790f467-65e5-4043-923d-14cd2da4c529/subagents/agent-acompact-51ea98d896d5f5d7.jsonl:L235, 875a1df5-d045-4fed-bd15-774cf1ce2337.jsonl:L302 (×6) | ✅ present | medium |  |
| `openComp` (onclick) | 37b9aba8-d807-4adf-b672-764e27067d0e.jsonl:L76, 9bb62f73-0e91-4b88-8263-95e8523b2238.jsonl:L1203, 9bb62f73-0e91-4b88-8263-95e8523b2238/subagents/agent-acompact-278d4915e57367f7.jsonl:L255 (×7) | ✅ present | medium |  |
| `openFullScreen` (onclick) | fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L2963, fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L2965, fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L2967 (×3) | ✅ present (new) | medium |  |
| `oSt` (onclick) | 0306b5a0-0173-4ce1-8e03-64e3cca07936.jsonl:L2464, 0306b5a0-0173-4ce1-8e03-64e3cca07936.jsonl:L2470, 0f6b5a8f-d645-4fb2-8123-64f4d239f8ce.jsonl:L117 (×26) | ✅ present | medium |  |
| `parseDate` (function) | 9bb62f73-0e91-4b88-8263-95e8523b2238.jsonl:L135, 9bb62f73-0e91-4b88-8263-95e8523b2238/subagents/agent-acompact-5d03aa71ce7b3960.jsonl:L134, 9bb62f73-0e91-4b88-8263-95e8523b2238/subagents/agent-aside_q… (×3) | ✅ present (new) | medium |  |
| `Peers in ${h.sec} — sorted by TE contribution` (card-title) | 9bb62f73-0e91-4b88-8263-95e8523b2238.jsonl:L875, 9bb62f73-0e91-4b88-8263-95e8523b2238/subagents/agent-acompact-f59e4390ac8d39a6.jsonl:L228, fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L2606 (×5) | ✅ present (new) | medium |  |
| `rankFilter` (id) | 0b5f4d42-6701-4c91-b48c-1175ffd26efa/subagents/agent-a619a31322509e7ca.jsonl:L120, 0f6b5a8f-d645-4fb2-8123-64f4d239f8ce.jsonl:L188, 875a1df5-d045-4fed-bd15-774cf1ce2337.jsonl:L174 (×7) | ✅ present | medium |  |
| `rbPieDiv` (id) | bf250eb0-8cb6-4c32-96f7-d26d443c8a97.jsonl:L1652, bf250eb0-8cb6-4c32-96f7-d26d443c8a97.jsonl:L1656, bf250eb0-8cb6-4c32-96f7-d26d443c8a97.jsonl:L1660 (×5) | ✅ present | medium |  |
| `rChr` (function) | 9bb62f73-0e91-4b88-8263-95e8523b2238.jsonl:L749, 9bb62f73-0e91-4b88-8263-95e8523b2238/subagents/agent-acompact-f59e4390ac8d39a6.jsonl:L103, bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompac… (×7) | ✅ present | medium |  |
| `Redwood Groups` (card-title) | 0306b5a0-0173-4ce1-8e03-64e3cca07936.jsonl:L1377, bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompact-2b2e69850cfd4eef.jsonl:L182, fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L748 (×3) | ✅ present | medium |  |
| `rExp` (function) | 875a1df5-d045-4fed-bd15-774cf1ce2337.jsonl:L130, 875a1df5-d045-4fed-bd15-774cf1ce2337/subagents/agent-acompact-36cc92af1a191d24.jsonl:L125, ba86eb57-dba7-45dc-b413-19e7cbec2c99.jsonl:L175 (×5) | ✅ present | medium |  |
| `rfbLblBoth` (id) | 0f6b5a8f-d645-4fb2-8123-64f4d239f8ce.jsonl:L128, 0f6b5a8f-d645-4fb2-8123-64f4d239f8ce/subagents/agent-acompact-840fe4766c4084ee.jsonl:L97, b2861e29-fdab-4386-a79d-886c89059725.jsonl:L376 (×8) | ✅ present (new) | medium |  |
| `rfbLblExp` (id) | 0f6b5a8f-d645-4fb2-8123-64f4d239f8ce.jsonl:L128, 0f6b5a8f-d645-4fb2-8123-64f4d239f8ce/subagents/agent-acompact-840fe4766c4084ee.jsonl:L97, b2861e29-fdab-4386-a79d-886c89059725.jsonl:L376 (×8) | ✅ present (new) | medium |  |
| `rfbLblTE` (id) | 0f6b5a8f-d645-4fb2-8123-64f4d239f8ce.jsonl:L128, 0f6b5a8f-d645-4fb2-8123-64f4d239f8ce/subagents/agent-acompact-840fe4766c4084ee.jsonl:L97, b2861e29-fdab-4386-a79d-886c89059725.jsonl:L376 (×8) | ✅ present (new) | medium |  |
| `rFRB` (function) | bf250eb0-8cb6-4c32-96f7-d26d443c8a97.jsonl:L1144, fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L313, fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L356 (×3) | ✅ present | medium |  |
| `rGroupTable` (function) | 0b5f4d42-6701-4c91-b48c-1175ffd26efa.jsonl:L196, 0b5f4d42-6701-4c91-b48c-1175ffd26efa/subagents/agent-acompact-df09ce4707361d21.jsonl:L194, 9bb62f73-0e91-4b88-8263-95e8523b2238.jsonl:L755 (×6) | ✅ present | medium |  |
| `Risk Budget Bars` (card-title) | bf250eb0-8cb6-4c32-96f7-d26d443c8a97.jsonl:L1652, bf250eb0-8cb6-4c32-96f7-d26d443c8a97.jsonl:L1656, bf250eb0-8cb6-4c32-96f7-d26d443c8a97.jsonl:L1660 (×4) | ✅ present | medium |  |
| `Risk Decomposition` (card-title) | 6790f467-65e5-4043-923d-14cd2da4c529.jsonl:L1416, 6790f467-65e5-4043-923d-14cd2da4c529/subagents/agent-acompact-51ea98d896d5f5d7.jsonl:L265 (×2) | ✅ present (new) | medium |  |
| `riskBudgetContent` (id) | bf250eb0-8cb6-4c32-96f7-d26d443c8a97.jsonl:L336, bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompact-2b2e69850cfd4eef.jsonl:L55, fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L1101 (×5) | ✅ present | medium |  |
| `riskExpHistDiv` (id) | 0f6b5a8f-d645-4fb2-8123-64f4d239f8ce.jsonl:L128, 0f6b5a8f-d645-4fb2-8123-64f4d239f8ce/subagents/agent-acompact-840fe4766c4084ee.jsonl:L97, 33df0d54-3b91-47b9-8d9b-71ad1f12c0c9.jsonl:L126 (×5) | ✅ present | medium |  |
| `riskFacBarDiv` (id) | 0f6b5a8f-d645-4fb2-8123-64f4d239f8ce.jsonl:L128, 0f6b5a8f-d645-4fb2-8123-64f4d239f8ce/subagents/agent-acompact-840fe4766c4084ee.jsonl:L97, 33df0d54-3b91-47b9-8d9b-71ad1f12c0c9.jsonl:L126 (×15) | ✅ present | medium |  |
| `rMCR` (function) | active-weight-treemap-spec.md:L122, active-weight-treemap-spec.md:L134, bf250eb0-8cb6-4c32-96f7-d26d443c8a97.jsonl:L942 (×7) | ✅ present | medium |  |
| `rRisk` (function) | 33df0d54-3b91-47b9-8d9b-71ad1f12c0c9.jsonl:L108, 33df0d54-3b91-47b9-8d9b-71ad1f12c0c9.jsonl:L126, b2861e29-fdab-4386-a79d-886c89059725.jsonl:L133 (×4) | ✅ present | medium |  |
| `rRiskFacBars` (function) | 9bb62f73-0e91-4b88-8263-95e8523b2238.jsonl:L894, 9bb62f73-0e91-4b88-8263-95e8523b2238/subagents/agent-acompact-f59e4390ac8d39a6.jsonl:L247, b2861e29-fdab-4386-a79d-886c89059725.jsonl:L133 (×10) | ✅ present (new) | medium |  |
| `rRiskFacBarsMode` (function) | b2861e29-fdab-4386-a79d-886c89059725.jsonl:L390, b2861e29-fdab-4386-a79d-886c89059725.jsonl:L767, b2861e29-fdab-4386-a79d-886c89059725.jsonl:L775 (×10) | ✅ present (new) | medium |  |
| `rRnk` (function) | 0b5f4d42-6701-4c91-b48c-1175ffd26efa/subagents/agent-a5ac9021ea6323712.jsonl:L100, 875a1df5-d045-4fed-bd15-774cf1ce2337.jsonl:L156, 875a1df5-d045-4fed-bd15-774cf1ce2337/subagents/agent-acompact-36cc92… (×8) | ✅ present | medium |  |
| `rRVQ` (function) | 9bb62f73-0e91-4b88-8263-95e8523b2238.jsonl:L721, 9bb62f73-0e91-4b88-8263-95e8523b2238.jsonl:L725, 9bb62f73-0e91-4b88-8263-95e8523b2238/subagents/agent-acompact-f59e4390ac8d39a6.jsonl:L75 (×4) | ✅ present (new) | medium |  |
| `rTEStackedArea` (function) | 9bb62f73-0e91-4b88-8263-95e8523b2238.jsonl:L148, 9bb62f73-0e91-4b88-8263-95e8523b2238/subagents/agent-acompact-5d03aa71ce7b3960.jsonl:L146, 9bb62f73-0e91-4b88-8263-95e8523b2238/subagents/agent-aside_q… (×8) | ✅ present (new) | medium |  |
| `rTree` (function) | active-weight-treemap-spec.md:L116, active-weight-treemap-spec.md:L122, active-weight-treemap-spec.md:L134 (×8) | ✅ present | medium |  |
| `rUnowned` (function) | 9bb62f73-0e91-4b88-8263-95e8523b2238.jsonl:L1625, bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompact-2b2e69850cfd4eef.jsonl:L79, fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L1805 (×3) | ✅ present | medium |  |
| `rUpdateCorr` (function) | b2861e29-fdab-4386-a79d-886c89059725.jsonl:L425, b2861e29-fdab-4386-a79d-886c89059725.jsonl:L648, b2861e29-fdab-4386-a79d-886c89059725/subagents/agent-acompact-7d364f7476edf88e.jsonl:L266 (×6) | ✅ present (new) | medium |  |
| `rWt` (function) | 0306b5a0-0173-4ce1-8e03-64e3cca07936.jsonl:L452, 0f6b5a8f-d645-4fb2-8123-64f4d239f8ce.jsonl:L117, 0f6b5a8f-d645-4fb2-8123-64f4d239f8ce/subagents/agent-acompact-840fe4766c4084ee.jsonl:L89 (×15) | ✅ present | medium |  |
| `saveConfig` (onclick) | 9bb62f73-0e91-4b88-8263-95e8523b2238.jsonl:L1184, 9bb62f73-0e91-4b88-8263-95e8523b2238/subagents/agent-acompact-278d4915e57367f7.jsonl:L236, bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompa… (×3) | ✅ present | medium |  |
| `screenshotCard` (onclick) | 0306b5a0-0173-4ce1-8e03-64e3cca07936.jsonl:L866, 0306b5a0-0173-4ce1-8e03-64e3cca07936.jsonl:L870, 0f6b5a8f-d645-4fb2-8123-64f4d239f8ce.jsonl:L188 (×26) | ✅ present | medium |  |
| `secFilter` (id) | 0b5f4d42-6701-4c91-b48c-1175ffd26efa/subagents/agent-a619a31322509e7ca.jsonl:L117, 0f6b5a8f-d645-4fb2-8123-64f4d239f8ce.jsonl:L188, 875a1df5-d045-4fed-bd15-774cf1ce2337.jsonl:L174 (×7) | ✅ present | medium |  |
| `setDataSrc` (function) | bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompact-2b2e69850cfd4eef.jsonl:L216, bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompact-2b2e69850cfd4eef.jsonl:L59, f168094b-9d6e-466e-… (×4) | ✅ present | medium |  |
| `setFacBarAll` (function) | 0f6b5a8f-d645-4fb2-8123-64f4d239f8ce.jsonl:L184, b2861e29-fdab-4386-a79d-886c89059725.jsonl:L779, b2861e29-fdab-4386-a79d-886c89059725/subagents/agent-acompact-c939e9da1245e709.jsonl:L191 (×5) | ✅ present (new) | medium |  |
| `setFacBarAll` (onclick) | 0f6b5a8f-d645-4fb2-8123-64f4d239f8ce.jsonl:L128, 0f6b5a8f-d645-4fb2-8123-64f4d239f8ce/subagents/agent-acompact-840fe4766c4084ee.jsonl:L97, 9bb62f73-0e91-4b88-8263-95e8523b2238.jsonl:L879 (×8) | ✅ present (new) | medium |  |
| `setFacExpAll` (onclick) | 0f6b5a8f-d645-4fb2-8123-64f4d239f8ce.jsonl:L128, 0f6b5a8f-d645-4fb2-8123-64f4d239f8ce/subagents/agent-acompact-840fe4766c4084ee.jsonl:L97, b2861e29-fdab-4386-a79d-886c89059725.jsonl:L133 (×4) | ✅ present (new) | medium |  |
| `setFacExpClear` (onclick) | 0f6b5a8f-d645-4fb2-8123-64f4d239f8ce.jsonl:L128, 0f6b5a8f-d645-4fb2-8123-64f4d239f8ce/subagents/agent-acompact-840fe4766c4084ee.jsonl:L97, b2861e29-fdab-4386-a79d-886c89059725.jsonl:L133 (×4) | ✅ present (new) | medium |  |
| `sortHold` (function) | 0306b5a0-0173-4ce1-8e03-64e3cca07936.jsonl:L1681, 0306b5a0-0173-4ce1-8e03-64e3cca07936.jsonl:L1689, 0306b5a0-0173-4ce1-8e03-64e3cca07936.jsonl:L1718 (×4) | ✅ present | medium |  |
| `sortTbl` (function) | 9bb62f73-0e91-4b88-8263-95e8523b2238.jsonl:L721, 9bb62f73-0e91-4b88-8263-95e8523b2238.jsonl:L725, 9bb62f73-0e91-4b88-8263-95e8523b2238/subagents/agent-acompact-f59e4390ac8d39a6.jsonl:L75 (×4) | ✅ present (new) | medium |  |
| `sortTbl` (onclick) | 0306b5a0-0173-4ce1-8e03-64e3cca07936.jsonl:L1539, 0306b5a0-0173-4ce1-8e03-64e3cca07936.jsonl:L1597, 0306b5a0-0173-4ce1-8e03-64e3cca07936.jsonl:L1602 (×41) | ✅ present (new) | medium |  |
| `stepWeek` (function) | 0b5f4d42-6701-4c91-b48c-1175ffd26efa.jsonl:L227, 0b5f4d42-6701-4c91-b48c-1175ffd26efa/subagents/agent-acompact-df09ce4707361d21.jsonl:L225, ba86eb57-dba7-45dc-b413-19e7cbec2c99.jsonl:L157 (×4) | ✅ present | medium |  |
| `stockHistDiv` (id) | 9bb62f73-0e91-4b88-8263-95e8523b2238.jsonl:L1480, 9bb62f73-0e91-4b88-8263-95e8523b2238.jsonl:L875, 9bb62f73-0e91-4b88-8263-95e8523b2238/subagents/agent-acompact-f59e4390ac8d39a6.jsonl:L228 (×5) | ✅ present | medium |  |
| `Subgroups` (card-title) | 9bb62f73-0e91-4b88-8263-95e8523b2238.jsonl:L1621, bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompact-2b2e69850cfd4eef.jsonl:L59, fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L841 (×3) | ✅ present | medium |  |
| `switchTab` (onclick) | 0f6b5a8f-d645-4fb2-8123-64f4d239f8ce.jsonl:L64, 0f6b5a8f-d645-4fb2-8123-64f4d239f8ce/subagents/agent-acompact-840fe4766c4084ee.jsonl:L51, 6790f467-65e5-4043-923d-14cd2da4c529.jsonl:L1287 (×4) | ✅ present | medium |  |
| `tabBar` (id) | 0f6b5a8f-d645-4fb2-8123-64f4d239f8ce.jsonl:L64, 0f6b5a8f-d645-4fb2-8123-64f4d239f8ce/subagents/agent-acompact-840fe4766c4084ee.jsonl:L51, 6790f467-65e5-4043-923d-14cd2da4c529.jsonl:L1287 (×6) | ✅ present | medium |  |
| `tbl-chr` (id) | 9bb62f73-0e91-4b88-8263-95e8523b2238.jsonl:L749, 9bb62f73-0e91-4b88-8263-95e8523b2238/subagents/agent-acompact-f59e4390ac8d39a6.jsonl:L103, portfolio-characteristics-spec.md:L101 (×5) | ✅ present (new) | medium |  |
| `tbl-fac` (id) | 0306b5a0-0173-4ce1-8e03-64e3cca07936.jsonl:L1551, 0306b5a0-0173-4ce1-8e03-64e3cca07936.jsonl:L576, 0306b5a0-0173-4ce1-8e03-64e3cca07936.jsonl:L887 (×10) | ✅ present (new) | medium |  |
| `tbl-grp` (id) | 0b5f4d42-6701-4c91-b48c-1175ffd26efa.jsonl:L196, 0b5f4d42-6701-4c91-b48c-1175ffd26efa/subagents/agent-acompact-df09ce4707361d21.jsonl:L194, 9bb62f73-0e91-4b88-8263-95e8523b2238.jsonl:L755 (×5) | ✅ present (new) | medium |  |
| `tbl-rnk` (id) | 0b5f4d42-6701-4c91-b48c-1175ffd26efa/subagents/agent-a5ac9021ea6323712.jsonl:L100, 9bb62f73-0e91-4b88-8263-95e8523b2238.jsonl:L746, 9bb62f73-0e91-4b88-8263-95e8523b2238/subagents/agent-acompact-f59e43… (×6) | ✅ present (new) | medium |  |
| `teStackedDiv` (id) | 0f6b5a8f-d645-4fb2-8123-64f4d239f8ce.jsonl:L128, 0f6b5a8f-d645-4fb2-8123-64f4d239f8ce/subagents/agent-acompact-840fe4766c4084ee.jsonl:L97, 33df0d54-3b91-47b9-8d9b-71ad1f12c0c9.jsonl:L126 (×6) | ✅ present | medium |  |
| `toggleConfig` (function) | 529c73ed-d7c3-4965-8e2a-33f7fef38298.jsonl:L68, 9bb62f73-0e91-4b88-8263-95e8523b2238.jsonl:L1215, 9bb62f73-0e91-4b88-8263-95e8523b2238/subagents/agent-acompact-278d4915e57367f7.jsonl:L267 (×4) | ✅ present | medium |  |
| `toggleConfig` (onclick) | 529c73ed-d7c3-4965-8e2a-33f7fef38298.jsonl:L71, bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompact-2b2e69850cfd4eef.jsonl:L47, f168094b-9d6e-466e-ba15-6b0f8cbc7c6e.jsonl:L318 (×3) | ✅ present | medium |  |
| `togglePresMode` (onclick) | 0306b5a0-0173-4ce1-8e03-64e3cca07936.jsonl:L2441, 9bb62f73-0e91-4b88-8263-95e8523b2238.jsonl:L1184, 9bb62f73-0e91-4b88-8263-95e8523b2238/subagents/agent-acompact-278d4915e57367f7.jsonl:L236 (×3) | ✅ present (new) | medium |  |
| `treeDiv` (id) | 0306b5a0-0173-4ce1-8e03-64e3cca07936.jsonl:L1169, active-weight-treemap-spec.md:L103, active-weight-treemap-spec.md:L95 (×5) | ✅ present | medium |  |
| `upd` (function) | 0f6b5a8f-d645-4fb2-8123-64f4d239f8ce.jsonl:L72, 0f6b5a8f-d645-4fb2-8123-64f4d239f8ce/subagents/agent-acompact-840fe4766c4084ee.jsonl:L57, 33df0d54-3b91-47b9-8d9b-71ad1f12c0c9.jsonl:L137 (×7) | ✅ present | medium |  |
| `updateTabBadges` (function) | 6790f467-65e5-4043-923d-14cd2da4c529.jsonl:L1295, 6790f467-65e5-4043-923d-14cd2da4c529/subagents/agent-acompact-51ea98d896d5f5d7.jsonl:L165, ba86eb57-dba7-45dc-b413-19e7cbec2c99.jsonl:L157 (×4) | ✅ present | medium |  |
| `upload` (function) | 37b9aba8-d807-4adf-b672-764e27067d0e.jsonl:L88, 6790f467-65e5-4043-923d-14cd2da4c529.jsonl:L1272, 6790f467-65e5-4043-923d-14cd2da4c529/subagents/agent-acompact-51ea98d896d5f5d7.jsonl:L148 (×3) | ✅ present | medium |  |
| `Weight History` (card-title) | 9bb62f73-0e91-4b88-8263-95e8523b2238.jsonl:L1480, bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompact-2b2e69850cfd4eef.jsonl:L131 (×2) | ✅ present | medium |  |
| Industry (cardIndustry) | TILE_SPEC.md Tier 3 #14 | 🤷 unclear | medium | Marked Building |
| Keyboard Shortcuts + Navigation | cli-prompts/keyboard-shortcuts-patch.md | ✅ present | medium |  |
| Quant Ranks (cardRanks) | TILE_SPEC.md Tier 3 #16 | ✅ present | medium |  |
| Responsive + Tablet/Mobile Polish | cli-prompts/responsive-mobile-patch.md | ✅ present | medium |  |
| setMapRegion on inline map (region zoom) | GAP_DISCOVERY.md example | ✅ present | medium |  |
| User Annotations + Notes System | cli-prompts/annotations-patch.md | ✅ present | medium |  |
| `cell` (function) | fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L2024 | ❌ missing | low |  |
| `charHistDiv` (id) | bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompact-2b2e69850cfd4eef.jsonl:L59 | ❌ missing (regressed) | low |  |
| `classifyRow` (function) | 37b9aba8-d807-4adf-b672-764e27067d0e.jsonl:L100 | ❌ missing (regressed) | low |  |
| `corrContent` (id) | bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompact-2b2e69850cfd4eef.jsonl:L55 | ❌ missing (regressed) | low |  |
| `drillHoldBarDiv` (id) | bf250eb0-8cb6-4c32-96f7-d26d443c8a97.jsonl:L356 | ❌ missing | low |  |
| `Factor Contributions to ${_fcLabel} TE` (card-title) | fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L834 | ❌ missing | low |  |
| `Factor Exposure Diff (${keys[0]} vs ${keys[1]})` (card-title) | bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompact-2b2e69850cfd4eef.jsonl:L107 | ❌ missing | low |  |
| `frbBudgetStrip` (id) | bf250eb0-8cb6-4c32-96f7-d26d443c8a97.jsonl:L1144 | ❌ missing | low |  |
| `frbShortName` (function) | bf250eb0-8cb6-4c32-96f7-d26d443c8a97.jsonl:L1431 | ❌ missing | low |  |
| `genFCorr` (function) | 9bb62f73-0e91-4b88-8263-95e8523b2238.jsonl:L417, 9bb62f73-0e91-4b88-8263-95e8523b2238/subagents/agent-acompact-fa5af12711981885.jsonl:L57 (×2) | ❌ missing (regressed) | low |  |
| `genHist` (function) | bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompact-2b2e69850cfd4eef.jsonl:L265 | ❌ missing (regressed) | low |  |
| `getGroup` (function) | 37b9aba8-d807-4adf-b672-764e27067d0e.jsonl:L100 | ❌ missing (regressed) | low |  |
| `hex2rgba` (function) | fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L2155 | ❌ missing | low |  |
| `metricSkipLabel` (id) | bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompact-2b2e69850cfd4eef.jsonl:L294, bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompact-2b2e69850cfd4eef.jsonl:L316 (×2) | ❌ missing | low |  |
| `metricSkipSlider` (id) | bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompact-2b2e69850cfd4eef.jsonl:L294, bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompact-2b2e69850cfd4eef.jsonl:L316 (×2) | ❌ missing | low |  |
| `onFacToggleChange` (function) | 33df0d54-3b91-47b9-8d9b-71ad1f12c0c9.jsonl:L108 | ❌ missing (regressed) | low |  |
| `Portfolio Context` (card-title) | bf250eb0-8cb6-4c32-96f7-d26d443c8a97.jsonl:L606 | ❌ missing | low |  |
| `rbSmallLegend` (id) | bf250eb0-8cb6-4c32-96f7-d26d443c8a97.jsonl:L1666 | ❌ missing | low |  |
| `refreshFacTable` (function) | 0306b5a0-0173-4ce1-8e03-64e3cca07936.jsonl:L916 | ❌ missing | low |  |
| `repairCommaInName` (function) | 37b9aba8-d807-4adf-b672-764e27067d0e.jsonl:L100 | ❌ missing (regressed) | low |  |
| `restoreSecSort` (function) | 0306b5a0-0173-4ce1-8e03-64e3cca07936.jsonl:L403 | ❌ missing | low |  |
| `rfbSegCtrl` (id) | 0f6b5a8f-d645-4fb2-8123-64f4d239f8ce.jsonl:L128, 0f6b5a8f-d645-4fb2-8123-64f4d239f8ce/subagents/agent-acompact-840fe4766c4084ee.jsonl:L97 (×2) | ❌ missing | low |  |
| `rRiskCharts` (function) | 33df0d54-3b91-47b9-8d9b-71ad1f12c0c9.jsonl:L126 | ❌ missing (regressed) | low |  |
| `rRiskFacSelectAll` (function) | 33df0d54-3b91-47b9-8d9b-71ad1f12c0c9.jsonl:L108 | ❌ missing (regressed) | low |  |
| `rRiskFacSelectAll` (onclick) | 33df0d54-3b91-47b9-8d9b-71ad1f12c0c9.jsonl:L126 | ❌ missing (regressed) | low |  |
| `rRiskFacToggleChart` (function) | 33df0d54-3b91-47b9-8d9b-71ad1f12c0c9.jsonl:L108 | ❌ missing (regressed) | low |  |
| `secChartBF` (id) | sector-active-weights-spec.md:L126 | ❌ missing | low |  |
| `secChartTM` (id) | sector-active-weights-spec.md:L126 | ❌ missing | low |  |
| `secChartWF` (id) | sector-active-weights-spec.md:L126 | ❌ missing | low |  |
| `setRegRankSrc` (function) | fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L722 | ❌ missing | low |  |
| `stockFacBarDiv` (id) | bf250eb0-8cb6-4c32-96f7-d26d443c8a97.jsonl:L606 | ❌ missing | low |  |
| `stratFullName` (id) | bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompact-2b2e69850cfd4eef.jsonl:L47 | ❌ missing (regressed) | low |  |
| `Unique to ${keys[0]} (top 10)` (card-title) | bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompact-2b2e69850cfd4eef.jsonl:L107 | ❌ missing | low |  |
| `Unique to ${keys[1]} (top 10)` (card-title) | bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompact-2b2e69850cfd4eef.jsonl:L107 | ❌ missing | low |  |
| `weeklyDatesFor` (function) | 37b9aba8-d807-4adf-b672-764e27067d0e.jsonl:L100 | ❌ missing (regressed) | low |  |
| `Weight History${h.sec?`` (card-title) | fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L983 | ❌ missing | low |  |
| `'+id+'` (id) | f168094b-9d6e-466e-ba15-6b0f8cbc7c6e.jsonl:L224 | ✅ present (new) | low |  |
| `'+searchId+'` (id) | fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L2929 | ✅ present (new) | low |  |
| `_riskAlertClick` (onclick) | fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L3049 | ✅ present (new) | low |  |
| `Active Share` (card-title) | b7818bde-fbfd-4187-a4c0-2518a1e4cbd0.jsonl:L120 | ✅ present | low |  |
| `applyHoldFilters` (function) | fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L3011, fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L575 (×2) | ✅ present | low |  |
| `applySectColVis` (function) | bf250eb0-8cb6-4c32-96f7-d26d443c8a97.jsonl:L165 | ✅ present (new) | low |  |
| `Bottom Exposed` (card-title) | bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompact-2b2e69850cfd4eef.jsonl:L127 | ✅ present | low |  |
| `buildCurrentSnap` (function) | fbae49d0-369a-42ae-8bee-3fbd440690f7.jsonl:L731 | ✅ present (new) | low |  |
| `buildPlotBg` (function) | fbae49d0-369a-42ae-8bee-3fbd440690f7.jsonl:L379 | ✅ present (new) | low |  |
| `cardChars` (id) | bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompact-2b2e69850cfd4eef.jsonl:L182 | ✅ present | low |  |
| `cardCorr` (id) | 875a1df5-d045-4fed-bd15-774cf1ce2337.jsonl:L145, 875a1df5-d045-4fed-bd15-774cf1ce2337/subagents/agent-acompact-36cc92af1a191d24.jsonl:L135, bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompac… (×3) | ✅ present | low |  |
| `cardFacDetail` (id) | 0306b5a0-0173-4ce1-8e03-64e3cca07936.jsonl:L866, 0306b5a0-0173-4ce1-8e03-64e3cca07936.jsonl:L870, bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompact-2b2e69850cfd4eef.jsonl:L182 (×3) | ✅ present | low |  |
| `cardFRB` (id) | bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompact-2b2e69850cfd4eef.jsonl:L182 | ✅ present | low |  |
| `cardGroups` (id) | 0306b5a0-0173-4ce1-8e03-64e3cca07936.jsonl:L1377, bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompact-2b2e69850cfd4eef.jsonl:L182, fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L748 (×3) | ✅ present | low |  |
| `cardMCR` (id) | bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompact-2b2e69850cfd4eef.jsonl:L182 | ✅ present | low |  |
| `cardRanks` (id) | bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompact-2b2e69850cfd4eef.jsonl:L182 | ✅ present | low |  |
| `cardRegions` (id) | 875a1df5-d045-4fed-bd15-774cf1ce2337.jsonl:L145, 875a1df5-d045-4fed-bd15-774cf1ce2337/subagents/agent-acompact-36cc92af1a191d24.jsonl:L135, bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompac… (×3) | ✅ present | low |  |
| `cardThisWeek` (id) | fbae49d0-369a-42ae-8bee-3fbd440690f7.jsonl:L1170 | ✅ present (new) | low |  |
| `cardUnowned` (id) | bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompact-2b2e69850cfd4eef.jsonl:L182 | ✅ present | low |  |
| `cardWatchlist` (id) | fbae49d0-369a-42ae-8bee-3fbd440690f7.jsonl:L826 | ✅ present (new) | low |  |
| `cfgApiKey` (id) | bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompact-2b2e69850cfd4eef.jsonl:L47 | ✅ present | low |  |
| `cfgApiUrl` (id) | bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompact-2b2e69850cfd4eef.jsonl:L47 | ✅ present | low |  |
| `cfgRefresh` (id) | bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompact-2b2e69850cfd4eef.jsonl:L47 | ✅ present | low |  |
| `cfgStratMap` (id) | bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompact-2b2e69850cfd4eef.jsonl:L47 | ✅ present | low |  |
| `charContent` (id) | bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompact-2b2e69850cfd4eef.jsonl:L55 | ✅ present | low |  |
| `clearHistory` (function) | 37b9aba8-d807-4adf-b672-764e27067d0e.jsonl:L100 | ✅ present | low |  |
| `clearHistory` (onclick) | 37b9aba8-d807-4adf-b672-764e27067d0e.jsonl:L100 | ✅ present | low |  |
| `closeAllModals` (function) | bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompact-2b2e69850cfd4eef.jsonl:L59, fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L2974 (×2) | ✅ present | low |  |
| `closeDrill` (function) | bf250eb0-8cb6-4c32-96f7-d26d443c8a97.jsonl:L364 | ✅ present | low |  |
| `closeHistPanel` (function) | 37b9aba8-d807-4adf-b672-764e27067d0e.jsonl:L100 | ✅ present | low |  |
| `compContent` (id) | bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompact-2b2e69850cfd4eef.jsonl:L55 | ✅ present | low |  |
| `configBtn` (id) | 529c73ed-d7c3-4965-8e2a-33f7fef38298.jsonl:L71, bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompact-2b2e69850cfd4eef.jsonl:L47, f168094b-9d6e-466e-ba15-6b0f8cbc7c6e.jsonl:L318 (×3) | ✅ present | low |  |
| `configPanel` (id) | bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompact-2b2e69850cfd4eef.jsonl:L47 | ✅ present | low |  |
| `connStatus` (id) | ba86eb57-dba7-45dc-b413-19e7cbec2c99.jsonl:L145, ba86eb57-dba7-45dc-b413-19e7cbec2c99/subagents/agent-acompact-37169388e782ab26.jsonl:L110, bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompac… (×3) | ✅ present | low |  |
| `content` (id) | 37b9aba8-d807-4adf-b672-764e27067d0e.jsonl:L84 | ✅ present | low |  |
| `copyBtn` (id) | 6790f467-65e5-4043-923d-14cd2da4c529.jsonl:L1341, 6790f467-65e5-4043-923d-14cd2da4c529/subagents/agent-acompact-51ea98d896d5f5d7.jsonl:L203 (×2) | ✅ present | low |  |
| `copySummary` (onclick) | 6790f467-65e5-4043-923d-14cd2da4c529.jsonl:L1341, 6790f467-65e5-4043-923d-14cd2da4c529/subagents/agent-acompact-51ea98d896d5f5d7.jsonl:L203 (×2) | ✅ present | low |  |
| `copyValue` (function) | bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompact-2b2e69850cfd4eef.jsonl:L59 | ✅ present | low |  |
| `Correlations` (card-title) | bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompact-2b2e69850cfd4eef.jsonl:L127 | ✅ present | low |  |
| `corrHeatPlot` (id) | b7818bde-fbfd-4187-a4c0-2518a1e4cbd0.jsonl:L134 | ✅ present (new) | low |  |
| `corrInsights` (id) | 0f6b5a8f-d645-4fb2-8123-64f4d239f8ce.jsonl:L128, 0f6b5a8f-d645-4fb2-8123-64f4d239f8ce/subagents/agent-acompact-840fe4766c4084ee.jsonl:L97, 33df0d54-3b91-47b9-8d9b-71ad1f12c0c9.jsonl:L126 (×4) | ✅ present | low |  |
| `Countries in ${name}` (card-title) | bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompact-2b2e69850cfd4eef.jsonl:L103 | ✅ present | low |  |
| `cycleFlag` (function) | fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L2993 | ✅ present (new) | low |  |
| `dataTimestamp` (id) | bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompact-2b2e69850cfd4eef.jsonl:L47 | ✅ present | low |  |
| `detectRiskAlerts` (function) | 0306b5a0-0173-4ce1-8e03-64e3cca07936.jsonl:L2437, fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L3049 (×2) | ✅ present (new) | low |  |
| `dismissWhatChanged` (function) | fbae49d0-369a-42ae-8bee-3fbd440690f7.jsonl:L1170, fbae49d0-369a-42ae-8bee-3fbd440690f7.jsonl:L731 (×2) | ✅ present (new) | low |  |
| `dismissWhatChanged` (onclick) | fbae49d0-369a-42ae-8bee-3fbd440690f7.jsonl:L731 | ✅ present (new) | low |  |
| `drillContent` (id) | bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompact-2b2e69850cfd4eef.jsonl:L55 | ✅ present | low |  |
| `drillHistDiv` (id) | 9bb62f73-0e91-4b88-8263-95e8523b2238.jsonl:L1008, 9bb62f73-0e91-4b88-8263-95e8523b2238/subagents/agent-acompact-278d4915e57367f7.jsonl:L61, bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompac… (×3) | ✅ present | low |  |
| `emptyState` (function) | bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompact-2b2e69850cfd4eef.jsonl:L212 | ✅ present | low |  |
| `exportCSV` (function) | bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompact-2b2e69850cfd4eef.jsonl:L59 | ✅ present | low |  |
| `facExpToggles` (id) | 0f6b5a8f-d645-4fb2-8123-64f4d239f8ce.jsonl:L128, 0f6b5a8f-d645-4fb2-8123-64f4d239f8ce/subagents/agent-acompact-840fe4766c4084ee.jsonl:L97, b2861e29-fdab-4386-a79d-886c89059725.jsonl:L133 (×4) | ✅ present (new) | low |  |
| `facTopTeStrip` (id) | fbae49d0-369a-42ae-8bee-3fbd440690f7.jsonl:L187 | ✅ present (new) | low |  |
| `facViewAll` (id) | 0306b5a0-0173-4ce1-8e03-64e3cca07936.jsonl:L866, 0306b5a0-0173-4ce1-8e03-64e3cca07936.jsonl:L870 (×2) | ✅ present (new) | low |  |
| `facViewPrimary` (id) | 0306b5a0-0173-4ce1-8e03-64e3cca07936.jsonl:L866, 0306b5a0-0173-4ce1-8e03-64e3cca07936.jsonl:L870 (×2) | ✅ present (new) | low |  |
| `facWaterfallDiv` (id) | 0306b5a0-0173-4ce1-8e03-64e3cca07936.jsonl:L653, b2861e29-fdab-4386-a79d-886c89059725.jsonl:L203, b2861e29-fdab-4386-a79d-886c89059725/subagents/agent-acompact-7d364f7476edf88e.jsonl:L59 (×3) | ✅ present (new) | low |  |
| `fetchFromAPI` (function) | bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompact-2b2e69850cfd4eef.jsonl:L59 | ✅ present | low |  |
| `filterByRank` (function) | bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompact-2b2e69850cfd4eef.jsonl:L115 | ✅ present | low |  |
| `filterHold` (function) | e62cfdfe-d20a-4c51-b748-89a29ac13385.jsonl:L27 | ✅ present | low |  |
| `frbDiv` (id) | bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompact-2b2e69850cfd4eef.jsonl:L111, bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompact-2b2e69850cfd4eef.jsonl:L182 (×2) | ✅ present | low |  |
| `fsChartDiv` (id) | fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L2910 | ✅ present (new) | low |  |
| `fsExplain` (id) | fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L2910 | ✅ present (new) | low |  |
| `fsFacHover` (function) | fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L2720, fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L2929 (×2) | ✅ present (new) | low |  |
| `fsFacUnhover` (function) | fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L2720, fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L2929 (×2) | ✅ present (new) | low |  |
| `fsPanelContent` (id) | fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L2910 | ✅ present (new) | low |  |
| `fsPanelTitle` (id) | fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L2910 | ✅ present (new) | low |  |
| `fsTitle` (id) | fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L2910 | ✅ present (new) | low |  |
| `generateShareURL` (function) | bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompact-2b2e69850cfd4eef.jsonl:L59 | ✅ present | low |  |
| `genHoldSummary` (function) | fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L2993 | ✅ present (new) | low |  |
| `getHistory` (function) | 37b9aba8-d807-4adf-b672-764e27067d0e.jsonl:L100 | ✅ present | low |  |
| `getHoldArchetype` (function) | fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L2993 | ✅ present (new) | low |  |
| `getNote` (function) | fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L2993 | ✅ present (new) | low |  |
| `getNotes` (function) | fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L2993 | ✅ present (new) | low |  |
| `getSelectedWeekSum` (function) | ba86eb57-dba7-45dc-b413-19e7cbec2c99.jsonl:L157, ba86eb57-dba7-45dc-b413-19e7cbec2c99/subagents/agent-acompact-37169388e782ab26.jsonl:L119 (×2) | ✅ present | low |  |
| `globalSearch` (function) | bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompact-2b2e69850cfd4eef.jsonl:L59 | ✅ present | low |  |
| `globalSearchInput` (id) | bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompact-2b2e69850cfd4eef.jsonl:L47 | ✅ present | low |  |
| `globalSearchResults` (id) | bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompact-2b2e69850cfd4eef.jsonl:L47 | ✅ present | low |  |
| `globalSearchWrap` (id) | bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompact-2b2e69850cfd4eef.jsonl:L47 | ✅ present | low |  |
| `glossaryBtn` (id) | f168094b-9d6e-466e-ba15-6b0f8cbc7c6e.jsonl:L318 | ✅ present (new) | low |  |
| `groupContent` (id) | bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompact-2b2e69850cfd4eef.jsonl:L55 | ✅ present | low |  |
| `grpTable` (id) | bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompact-2b2e69850cfd4eef.jsonl:L182, fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L748 (×2) | ✅ present | low |  |
| `histBtn` (id) | 37b9aba8-d807-4adf-b672-764e27067d0e.jsonl:L76 | ✅ present | low |  |
| `histPanel` (id) | 37b9aba8-d807-4adf-b672-764e27067d0e.jsonl:L76 | ✅ present | low |  |
| `histWrap` (id) | 37b9aba8-d807-4adf-b672-764e27067d0e.jsonl:L76 | ✅ present | low |  |
| `init` (function) | bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompact-2b2e69850cfd4eef.jsonl:L91 | ✅ present | low |  |
| `isoDate` (function) | 0b5f4d42-6701-4c91-b48c-1175ffd26efa.jsonl:L189, 0b5f4d42-6701-4c91-b48c-1175ffd26efa/subagents/agent-acompact-df09ce4707361d21.jsonl:L188, 9bb62f73-0e91-4b88-8263-95e8523b2238.jsonl:L135 (×5) | ✅ present (new) | low |  |
| `jumpToLatest` (onclick) | ba86eb57-dba7-45dc-b413-19e7cbec2c99.jsonl:L145, ba86eb57-dba7-45dc-b413-19e7cbec2c99/subagents/agent-acompact-37169388e782ab26.jsonl:L110 (×2) | ✅ present | low |  |
| `latestBtn` (id) | ba86eb57-dba7-45dc-b413-19e7cbec2c99.jsonl:L145, ba86eb57-dba7-45dc-b413-19e7cbec2c99/subagents/agent-acompact-37169388e782ab26.jsonl:L110 (×2) | ✅ present | low |  |
| `loadConfig` (function) | bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompact-2b2e69850cfd4eef.jsonl:L59 | ✅ present | low |  |
| `loadFromHistory` (function) | 37b9aba8-d807-4adf-b672-764e27067d0e.jsonl:L100 | ✅ present | low |  |
| `loadFromHistory` (onclick) | 37b9aba8-d807-4adf-b672-764e27067d0e.jsonl:L100 | ✅ present | low |  |
| `loadHoldFlags` (function) | fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L2993 | ✅ present (new) | low |  |
| `loadHoldSnap` (function) | fbae49d0-369a-42ae-8bee-3fbd440690f7.jsonl:L731 | ✅ present (new) | low |  |
| `loadHoldSnapDismissed` (function) | fbae49d0-369a-42ae-8bee-3fbd440690f7.jsonl:L731 | ✅ present (new) | low |  |
| `mapRegionBtns` (id) | fbae49d0-369a-42ae-8bee-3fbd440690f7.jsonl:L1625 | ✅ present (new) | low |  |
| `mapSecondary` (id) | fbae49d0-369a-42ae-8bee-3fbd440690f7.jsonl:L1625 | ✅ present (new) | low |  |
| `Marginal Contribution to Risk (Top & Bottom)` (card-title) | fbae49d0-369a-42ae-8bee-3fbd440690f7.jsonl:L1256 | ✅ present (new) | low |  |
| `MCR vs TE Contribution` (card-title) | fbae49d0-369a-42ae-8bee-3fbd440690f7.jsonl:L1243 | ✅ present (new) | low |  |
| `mcrDiv` (id) | bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompact-2b2e69850cfd4eef.jsonl:L111, bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompact-2b2e69850cfd4eef.jsonl:L182 (×2) | ✅ present | low |  |
| `metricChartDiv` (id) | bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompact-2b2e69850cfd4eef.jsonl:L294, bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompact-2b2e69850cfd4eef.jsonl:L316, bf720b9d-9e2c-41d7… (×3) | ✅ present | low |  |
| `metricContent` (id) | bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompact-2b2e69850cfd4eef.jsonl:L55 | ✅ present | low |  |
| `mkNode` (function) | f168094b-9d6e-466e-ba15-6b0f8cbc7c6e.jsonl:L224 | ✅ present (new) | low |  |
| `My Watchlist (${total})` (card-title) | fbae49d0-369a-42ae-8bee-3fbd440690f7.jsonl:L826 | ✅ present (new) | low |  |
| `neutDelta` (function) | 875a1df5-d045-4fed-bd15-774cf1ce2337.jsonl:L130, 875a1df5-d045-4fed-bd15-774cf1ce2337/subagents/agent-acompact-36cc92af1a191d24.jsonl:L125 (×2) | ✅ present | low |  |
| `normalize` (function) | 6d426492-6b5c-4be6-8f3f-5650d336c8e4.jsonl:L29, 9bb62f73-0e91-4b88-8263-95e8523b2238.jsonl:L1360 (×2) | ✅ present | low |  |
| `normalizeFactSet` (function) | bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompact-2b2e69850cfd4eef.jsonl:L212 | ✅ present | low |  |
| `oDrChar` (function) | bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompact-2b2e69850cfd4eef.jsonl:L59 | ✅ present | low |  |
| `oDrFRisk` (function) | ba86eb57-dba7-45dc-b413-19e7cbec2c99.jsonl:L241 | ✅ present | low |  |
| `oDrRiskBudget` (function) | bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompact-2b2e69850cfd4eef.jsonl:L59 | ✅ present | low |  |
| `oDrRiskBudget` (onclick) | bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompact-2b2e69850cfd4eef.jsonl:L111, bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompact-2b2e69850cfd4eef.jsonl:L182 (×2) | ✅ present | low |  |
| `oDrS` (function) | ba86eb57-dba7-45dc-b413-19e7cbec2c99.jsonl:L260 | ✅ present | low |  |
| `oDrS` (onclick) | ba86eb57-dba7-45dc-b413-19e7cbec2c99.jsonl:L260, bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompact-2b2e69850cfd4eef.jsonl:L63 (×2) | ✅ present | low |  |
| `oDrUnowned` (function) | bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompact-2b2e69850cfd4eef.jsonl:L59 | ✅ present | low |  |
| `openFullScreen` (function) | fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L2929 | ✅ present (new) | low |  |
| `openGlossary` (function) | f168094b-9d6e-466e-ba15-6b0f8cbc7c6e.jsonl:L322 | ✅ present (new) | low |  |
| `openGlossary` (onclick) | f168094b-9d6e-466e-ba15-6b0f8cbc7c6e.jsonl:L318, f168094b-9d6e-466e-ba15-6b0f8cbc7c6e.jsonl:L322 (×2) | ✅ present (new) | low |  |
| `openReport` (onclick) | bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompact-2b2e69850cfd4eef.jsonl:L47 | ✅ present | low |  |
| `oSt` (function) | 9bb62f73-0e91-4b88-8263-95e8523b2238.jsonl:L875, 9bb62f73-0e91-4b88-8263-95e8523b2238/subagents/agent-acompact-f59e4390ac8d39a6.jsonl:L228 (×2) | ✅ present | low |  |
| `parseFactSetCSV` (function) | 37b9aba8-d807-4adf-b672-764e27067d0e.jsonl:L100 | ✅ present | low |  |
| `Portfolio Characteristics` (card-title) | bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompact-2b2e69850cfd4eef.jsonl:L182 | ✅ present | low |  |
| `Portfolio Summary` (card-title) | bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompact-2b2e69850cfd4eef.jsonl:L316 | ✅ present | low |  |
| `precFull` (id) | 9bb62f73-0e91-4b88-8263-95e8523b2238.jsonl:L1184, 9bb62f73-0e91-4b88-8263-95e8523b2238/subagents/agent-acompact-278d4915e57367f7.jsonl:L236 (×2) | ✅ present (new) | low |  |
| `precStd` (id) | 9bb62f73-0e91-4b88-8263-95e8523b2238.jsonl:L1184, 9bb62f73-0e91-4b88-8263-95e8523b2238/subagents/agent-acompact-278d4915e57367f7.jsonl:L236 (×2) | ✅ present (new) | low |  |
| `presMode` (id) | 0306b5a0-0173-4ce1-8e03-64e3cca07936.jsonl:L2441, 9bb62f73-0e91-4b88-8263-95e8523b2238.jsonl:L1184, 9bb62f73-0e91-4b88-8263-95e8523b2238/subagents/agent-acompact-278d4915e57367f7.jsonl:L236 (×3) | ✅ present (new) | low |  |
| `presModeStatus` (id) | 0306b5a0-0173-4ce1-8e03-64e3cca07936.jsonl:L2441, 9bb62f73-0e91-4b88-8263-95e8523b2238.jsonl:L1184, 9bb62f73-0e91-4b88-8263-95e8523b2238/subagents/agent-acompact-278d4915e57367f7.jsonl:L236 (×3) | ✅ present (new) | low |  |
| `profAlert` (id) | 9bb62f73-0e91-4b88-8263-95e8523b2238.jsonl:L879, 9bb62f73-0e91-4b88-8263-95e8523b2238/subagents/agent-acompact-f59e4390ac8d39a6.jsonl:L232 (×2) | ✅ present (new) | low |  |
| `Quant Ranks` (card-title) | bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompact-2b2e69850cfd4eef.jsonl:L182 | ✅ present | low |  |
| `Quant Scores` (card-title) | bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompact-2b2e69850cfd4eef.jsonl:L131 | ✅ present | low |  |
| `rankDistDiv` (id) | 875a1df5-d045-4fed-bd15-774cf1ce2337.jsonl:L174, 875a1df5-d045-4fed-bd15-774cf1ce2337/subagents/agent-acompact-36cc92af1a191d24.jsonl:L156, holdings-tab-spec.md:L68 (×3) | ✅ present | low |  |
| `rbBarDiv` (id) | bf250eb0-8cb6-4c32-96f7-d26d443c8a97.jsonl:L1652, bf250eb0-8cb6-4c32-96f7-d26d443c8a97.jsonl:L1656, bf250eb0-8cb6-4c32-96f7-d26d443c8a97.jsonl:L1660 (×4) | ✅ present | low |  |
| `refreshCardNoteBadges` (function) | fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L2993 | ✅ present (new) | low |  |
| `refreshDataStamp` (function) | fbae49d0-369a-42ae-8bee-3fbd440690f7.jsonl:L674 | ✅ present (new) | low |  |
| `refreshStratSel` (function) | 9bb62f73-0e91-4b88-8263-95e8523b2238.jsonl:L1218, 9bb62f73-0e91-4b88-8263-95e8523b2238/subagents/agent-acompact-278d4915e57367f7.jsonl:L270 (×2) | ✅ present (new) | low |  |
| `renderFsFactorMap` (function) | fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L2929 | ✅ present (new) | low |  |
| `reportBtn` (id) | bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompact-2b2e69850cfd4eef.jsonl:L47 | ✅ present | low |  |
| `reportContent` (id) | bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompact-2b2e69850cfd4eef.jsonl:L55 | ✅ present | low |  |
| `reupload` (id) | 37b9aba8-d807-4adf-b672-764e27067d0e.jsonl:L76, bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompact-2b2e69850cfd4eef.jsonl:L47 (×2) | ✅ present | low |  |
| `rGroupChart` (function) | fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L759 | ✅ present | low |  |
| `rHoldConc` (function) | bf250eb0-8cb6-4c32-96f7-d26d443c8a97.jsonl:L1589, fbae49d0-369a-42ae-8bee-3fbd440690f7.jsonl:L116 (×2) | ✅ present | low |  |
| `Risk Decomposition Tree` (card-title) | f168094b-9d6e-466e-ba15-6b0f8cbc7c6e.jsonl:L224 | ✅ present (new) | low |  |
| `riskAlertsBanner` (id) | fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L3049 | ✅ present (new) | low |  |
| `riskAlertsBannerHtml` (function) | fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L3049 | ✅ present (new) | low |  |
| `riskDelta` (function) | 875a1df5-d045-4fed-bd15-774cf1ce2337.jsonl:L130, 875a1df5-d045-4fed-bd15-774cf1ce2337/subagents/agent-acompact-36cc92af1a191d24.jsonl:L125 (×2) | ✅ present | low |  |
| `riskFacHistDiv` (id) | 875a1df5-d045-4fed-bd15-774cf1ce2337.jsonl:L259, ba86eb57-dba7-45dc-b413-19e7cbec2c99.jsonl:L241 (×2) | ✅ present | low |  |
| `riskFacRetDiv` (id) | 875a1df5-d045-4fed-bd15-774cf1ce2337.jsonl:L259 | ✅ present | low |  |
| `rRankDist` (function) | bf250eb0-8cb6-4c32-96f7-d26d443c8a97.jsonl:L1587 | ✅ present | low |  |
| `saveConfig` (function) | bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompact-2b2e69850cfd4eef.jsonl:L59 | ✅ present | low |  |
| `saveHoldFlags` (function) | fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L2993 | ✅ present (new) | low |  |
| `saveHoldSnap` (function) | fbae49d0-369a-42ae-8bee-3fbd440690f7.jsonl:L731 | ✅ present (new) | low |  |
| `saveHoldSnapDismissed` (function) | fbae49d0-369a-42ae-8bee-3fbd440690f7.jsonl:L731 | ✅ present (new) | low |  |
| `saveToHistory` (function) | 37b9aba8-d807-4adf-b672-764e27067d0e.jsonl:L100 | ✅ present | low |  |
| `sAvg` (function) | fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L732 | ✅ present (new) | low |  |
| `screenshotCard` (function) | bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompact-2b2e69850cfd4eef.jsonl:L59 | ✅ present | low |  |
| `searchHold` (function) | e62cfdfe-d20a-4c51-b748-89a29ac13385.jsonl:L27, fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L327 (×2) | ✅ present | low |  |
| `secChart` (id) | 875a1df5-d045-4fed-bd15-774cf1ce2337.jsonl:L135, 875a1df5-d045-4fed-bd15-774cf1ce2337/subagents/agent-acompact-36cc92af1a191d24.jsonl:L128, bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompac… (×4) | ✅ present | low |  |
| `secChartDiv` (id) | 875a1df5-d045-4fed-bd15-774cf1ce2337.jsonl:L135, 875a1df5-d045-4fed-bd15-774cf1ce2337/subagents/agent-acompact-36cc92af1a191d24.jsonl:L128, bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompac… (×4) | ✅ present | low |  |
| `secHeatColor` (function) | 6790f467-65e5-4043-923d-14cd2da4c529.jsonl:L1384, 6790f467-65e5-4043-923d-14cd2da4c529/subagents/agent-acompact-51ea98d896d5f5d7.jsonl:L238 (×2) | ✅ present | low |  |
| `secTable` (id) | 875a1df5-d045-4fed-bd15-774cf1ce2337.jsonl:L135, 875a1df5-d045-4fed-bd15-774cf1ce2337/subagents/agent-acompact-36cc92af1a191d24.jsonl:L128, bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompac… (×3) | ✅ present | low |  |
| `setDataSrc` (onclick) | bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompact-2b2e69850cfd4eef.jsonl:L47 | ✅ present | low |  |
| `setFacExpAll` (function) | b2861e29-fdab-4386-a79d-886c89059725.jsonl:L133, b2861e29-fdab-4386-a79d-886c89059725/subagents/agent-acompact-9d785f21d8fa6596.jsonl:L67 (×2) | ✅ present (new) | low |  |
| `setFacExpClear` (function) | b2861e29-fdab-4386-a79d-886c89059725.jsonl:L133, b2861e29-fdab-4386-a79d-886c89059725/subagents/agent-acompact-9d785f21d8fa6596.jsonl:L67 (×2) | ✅ present (new) | low |  |
| `setFacGroup` (function) | 9bb62f73-0e91-4b88-8263-95e8523b2238.jsonl:L894, 9bb62f73-0e91-4b88-8263-95e8523b2238/subagents/agent-acompact-f59e4390ac8d39a6.jsonl:L247 (×2) | ✅ present (new) | low |  |
| `setFacGroup` (onclick) | 9bb62f73-0e91-4b88-8263-95e8523b2238.jsonl:L879, 9bb62f73-0e91-4b88-8263-95e8523b2238/subagents/agent-acompact-f59e4390ac8d39a6.jsonl:L232 (×2) | ✅ present (new) | low |  |
| `setFacView` (function) | bf250eb0-8cb6-4c32-96f7-d26d443c8a97.jsonl:L696 | ✅ present (new) | low |  |
| `setFacView` (onclick) | 0306b5a0-0173-4ce1-8e03-64e3cca07936.jsonl:L866, 0306b5a0-0173-4ce1-8e03-64e3cca07936.jsonl:L870 (×2) | ✅ present (new) | low |  |
| `setFsMapColor` (function) | fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L2929 | ✅ present (new) | low |  |
| `setFsMapColor` (onclick) | fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L2929 | ✅ present (new) | low |  |
| `setFsMapRegion` (function) | fbae49d0-369a-42ae-8bee-3fbd440690f7.jsonl:L1639, fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L2929 (×2) | ✅ present (new) | low |  |
| `setFsMapRegion` (onclick) | fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L2929 | ✅ present (new) | low |  |
| `setMapRegion` (function) | 0306b5a0-0173-4ce1-8e03-64e3cca07936.jsonl:L1913, fbae49d0-369a-42ae-8bee-3fbd440690f7.jsonl:L1628 (×2) | ✅ present (new) | low |  |
| `setMapRegion` (onclick) | fbae49d0-369a-42ae-8bee-3fbd440690f7.jsonl:L1625 | ✅ present (new) | low |  |
| `setNote` (function) | fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L2993 | ✅ present (new) | low |  |
| `shareBtn` (id) | 6790f467-65e5-4043-923d-14cd2da4c529.jsonl:L1341, 6790f467-65e5-4043-923d-14cd2da4c529/subagents/agent-acompact-51ea98d896d5f5d7.jsonl:L203, bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompa… (×3) | ✅ present | low |  |
| `showLoading` (function) | bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompact-2b2e69850cfd4eef.jsonl:L59 | ✅ present | low |  |
| `showNotePopup` (function) | fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L2993 | ✅ present (new) | low |  |
| `showToast` (function) | bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompact-2b2e69850cfd4eef.jsonl:L212 | ✅ present | low |  |
| `showValidPanel` (function) | 37b9aba8-d807-4adf-b672-764e27067d0e.jsonl:L100 | ✅ present | low |  |
| `srcFile` (id) | bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompact-2b2e69850cfd4eef.jsonl:L47 | ✅ present | low |  |
| `srcLive` (id) | bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompact-2b2e69850cfd4eef.jsonl:L47 | ✅ present | low |  |
| `startLiveRefresh` (function) | bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompact-2b2e69850cfd4eef.jsonl:L212 | ✅ present | low |  |
| `stepWeek` (onclick) | ba86eb57-dba7-45dc-b413-19e7cbec2c99.jsonl:L145, ba86eb57-dba7-45dc-b413-19e7cbec2c99/subagents/agent-acompact-37169388e782ab26.jsonl:L110 (×2) | ✅ present | low |  |
| `stockContent` (id) | bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompact-2b2e69850cfd4eef.jsonl:L55 | ✅ present | low |  |
| `stratSel` (id) | bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompact-2b2e69850cfd4eef.jsonl:L47 | ✅ present | low |  |
| `sumDrillDiv` (id) | ba86eb57-dba7-45dc-b413-19e7cbec2c99.jsonl:L260 | ✅ present | low |  |
| `tab-exposures` (id) | 0f6b5a8f-d645-4fb2-8123-64f4d239f8ce.jsonl:L68, 0f6b5a8f-d645-4fb2-8123-64f4d239f8ce/subagents/agent-acompact-840fe4766c4084ee.jsonl:L54, 37b9aba8-d807-4adf-b672-764e27067d0e.jsonl:L84 (×3) | ✅ present | low |  |
| `tab-risk` (id) | 0f6b5a8f-d645-4fb2-8123-64f4d239f8ce.jsonl:L68, 0f6b5a8f-d645-4fb2-8123-64f4d239f8ce/subagents/agent-acompact-840fe4766c4084ee.jsonl:L54 (×2) | ✅ present | low |  |
| `tbl-cmp` (id) | 9bb62f73-0e91-4b88-8263-95e8523b2238.jsonl:L1203, 9bb62f73-0e91-4b88-8263-95e8523b2238/subagents/agent-acompact-278d4915e57367f7.jsonl:L255 (×2) | ✅ present (new) | low |  |
| `tbl-fac-wrap` (id) | bf250eb0-8cb6-4c32-96f7-d26d443c8a97.jsonl:L699, fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L2123 (×2) | ✅ present (new) | low |  |
| `tbl-unowned` (id) | 9bb62f73-0e91-4b88-8263-95e8523b2238.jsonl:L1625, fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L1805 (×2) | ✅ present (new) | low |  |
| `This Week \u2014 ${s.name\|\|s.id}` (card-title) | fbae49d0-369a-42ae-8bee-3fbd440690f7.jsonl:L1170 | ✅ present (new) | low |  |
| `thisWeekCardHtml` (function) | fbae49d0-369a-42ae-8bee-3fbd440690f7.jsonl:L1170 | ✅ present (new) | low |  |
| `thr_asDeltaMin` (id) | 529c73ed-d7c3-4965-8e2a-33f7fef38298.jsonl:L63, fbae49d0-369a-42ae-8bee-3fbd440690f7.jsonl:L672 (×2) | ✅ present (new) | low |  |
| `thr_factorSigma` (id) | 529c73ed-d7c3-4965-8e2a-33f7fef38298.jsonl:L63 | ✅ present (new) | low |  |
| `thr_freshAmberDays` (id) | fbae49d0-369a-42ae-8bee-3fbd440690f7.jsonl:L672 | ✅ present (new) | low |  |
| `thr_freshRedDays` (id) | fbae49d0-369a-42ae-8bee-3fbd440690f7.jsonl:L672 | ✅ present (new) | low |  |
| `thr_q5WeightMax` (id) | 529c73ed-d7c3-4965-8e2a-33f7fef38298.jsonl:L63 | ✅ present (new) | low |  |
| `thr_singleNameTE` (id) | 529c73ed-d7c3-4965-8e2a-33f7fef38298.jsonl:L63 | ✅ present (new) | low |  |
| `thr_teAmber` (id) | 529c73ed-d7c3-4965-8e2a-33f7fef38298.jsonl:L63 | ✅ present (new) | low |  |
| `thr_teRed` (id) | 529c73ed-d7c3-4965-8e2a-33f7fef38298.jsonl:L63 | ✅ present (new) | low |  |
| `toggleDtNode` (function) | f168094b-9d6e-466e-ba15-6b0f8cbc7c6e.jsonl:L224 | ✅ present (new) | low |  |
| `toggleDtNode` (onclick) | f168094b-9d6e-466e-ba15-6b0f8cbc7c6e.jsonl:L224 | ✅ present (new) | low |  |
| `toggleFlaggedFilter` (function) | fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L3011 | ✅ present (new) | low |  |
| `toggleFlaggedFilter` (onclick) | fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L3000 | ✅ present (new) | low |  |
| `toggleGrpView` (function) | fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L767 | ✅ present | low |  |
| `toggleGrpView` (onclick) | bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompact-2b2e69850cfd4eef.jsonl:L182, fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L748 (×2) | ✅ present | low |  |
| `toggleHistPanel` (function) | 37b9aba8-d807-4adf-b672-764e27067d0e.jsonl:L100 | ✅ present | low |  |
| `toggleHistPanel` (onclick) | 37b9aba8-d807-4adf-b672-764e27067d0e.jsonl:L76 | ✅ present | low |  |
| `togglePinned` (function) | 9bb62f73-0e91-4b88-8263-95e8523b2238.jsonl:L1218, 9bb62f73-0e91-4b88-8263-95e8523b2238/subagents/agent-acompact-278d4915e57367f7.jsonl:L270 (×2) | ✅ present (new) | low |  |
| `togglePresMode` (function) | 9bb62f73-0e91-4b88-8263-95e8523b2238.jsonl:L1218, 9bb62f73-0e91-4b88-8263-95e8523b2238/subagents/agent-acompact-278d4915e57367f7.jsonl:L270 (×2) | ✅ present (new) | low |  |
| `toggleShortcutHelp` (function) | f168094b-9d6e-466e-ba15-6b0f8cbc7c6e.jsonl:L269 | ✅ present (new) | low |  |
| `toggleShortcutHelp` (onclick) | f168094b-9d6e-466e-ba15-6b0f8cbc7c6e.jsonl:L269 | ✅ present (new) | low |  |
| `toggleValidPanel` (function) | 37b9aba8-d807-4adf-b672-764e27067d0e.jsonl:L100 | ✅ present | low |  |
| `toggleValidPanel` (onclick) | 37b9aba8-d807-4adf-b672-764e27067d0e.jsonl:L100 | ✅ present | low |  |
| `Top 10 Benchmark Weights` (card-title) | bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompact-2b2e69850cfd4eef.jsonl:L316 | ✅ present | low |  |
| `Top Exposed` (card-title) | bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompact-2b2e69850cfd4eef.jsonl:L127 | ✅ present | low |  |
| `Unowned Risk Contributors` (card-title) | bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompact-2b2e69850cfd4eef.jsonl:L182 | ✅ present | low |  |
| `unownedContent` (id) | bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompact-2b2e69850cfd4eef.jsonl:L55 | ✅ present | low |  |
| `updateHistButton` (function) | 37b9aba8-d807-4adf-b672-764e27067d0e.jsonl:L100 | ✅ present | low |  |
| `updateHistUI` (function) | 37b9aba8-d807-4adf-b672-764e27067d0e.jsonl:L100 | ✅ present | low |  |
| `uploadZone` (id) | 37b9aba8-d807-4adf-b672-764e27067d0e.jsonl:L80 | ✅ present | low |  |
| `uploadZoneText` (id) | 37b9aba8-d807-4adf-b672-764e27067d0e.jsonl:L80 | ✅ present | low |  |
| `validBody` (id) | 37b9aba8-d807-4adf-b672-764e27067d0e.jsonl:L100 | ✅ present | low |  |
| `validPanel` (id) | 37b9aba8-d807-4adf-b672-764e27067d0e.jsonl:L84 | ✅ present | low |  |
| `validToggle` (id) | 37b9aba8-d807-4adf-b672-764e27067d0e.jsonl:L100 | ✅ present | low |  |
| `watchlistCardHtml` (function) | fbae49d0-369a-42ae-8bee-3fbd440690f7.jsonl:L826 | ✅ present (new) | low |  |
| `weekBannerHtml` (function) | ba86eb57-dba7-45dc-b413-19e7cbec2c99.jsonl:L157, ba86eb57-dba7-45dc-b413-19e7cbec2c99/subagents/agent-acompact-37169388e782ab26.jsonl:L119 (×2) | ✅ present | low |  |
| `weekSel` (id) | ba86eb57-dba7-45dc-b413-19e7cbec2c99.jsonl:L145, ba86eb57-dba7-45dc-b413-19e7cbec2c99/subagents/agent-acompact-37169388e782ab26.jsonl:L110 (×2) | ✅ present | low |  |
| `weekSelWrap` (id) | 0b5f4d42-6701-4c91-b48c-1175ffd26efa/subagents/agent-a619a31322509e7ca.jsonl:L147, ba86eb57-dba7-45dc-b413-19e7cbec2c99.jsonl:L145, ba86eb57-dba7-45dc-b413-19e7cbec2c99/subagents/agent-acompact-371693… (×3) | ✅ present | low |  |
| `whatChangedBanner` (id) | 0306b5a0-0173-4ce1-8e03-64e3cca07936.jsonl:L2464, 0306b5a0-0173-4ce1-8e03-64e3cca07936.jsonl:L2470, fbae49d0-369a-42ae-8bee-3fbd440690f7.jsonl:L731 (×3) | ✅ present (new) | low |  |
| `whatChangedBannerHtml` (function) | fbae49d0-369a-42ae-8bee-3fbd440690f7.jsonl:L731 | ✅ present (new) | low |  |
| `Why This Stock Matters` (card-title) | bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompact-2b2e69850cfd4eef.jsonl:L59 | ✅ present | low |  |

### modals

| Feature | Source(s) | Status | Priority | Notes |
|---|---|---|---|---|
| `riskBudgetModal` (id) | bf250eb0-8cb6-4c32-96f7-d26d443c8a97.jsonl:L336, bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompact-2b2e69850cfd4eef.jsonl:L55, fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L1101 (×5) | ✅ present | medium |  |
| oDr — sector/region drill | TILE_SPEC.md drill modals | 🤷 unclear | medium |  |
| oDrChar — characteristic time series | TILE_SPEC.md drill modals | 🤷 unclear | medium |  |
| oDrCountry — country drill | TILE_SPEC.md drill modals | 🤷 unclear | medium |  |
| oDrFRisk — factor time series drill | TILE_SPEC.md drill modals | 🤷 unclear | medium |  |
| oDrGroup — Redwood group drill | TILE_SPEC.md drill modals | 🤷 unclear | medium |  |
| oDrMetric modal | TILE_SPEC.md drill modals | 🤷 unclear | medium |  |
| oDrRiskBudget — factor risk budget drill | TILE_SPEC.md drill modals | 🤷 unclear | medium |  |
| oDrUnowned — unowned security drill | TILE_SPEC.md drill modals | 🤷 unclear | medium |  |
| oSt — stock detail modal | TILE_SPEC.md drill modals | 🤷 unclear | medium |  |
| `attrDrillContent` (id) | bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompact-2b2e69850cfd4eef.jsonl:L55 | ❌ missing (regressed) | low |  |
| `attrDrillModal` (id) | bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompact-2b2e69850cfd4eef.jsonl:L55 | ❌ missing (regressed) | low |  |
| `corrModal` (id) | bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompact-2b2e69850cfd4eef.jsonl:L55 | ❌ missing (regressed) | low |  |
| `charModal` (id) | bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompact-2b2e69850cfd4eef.jsonl:L55 | ✅ present | low |  |
| `closeFsModal` (function) | fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L2929 | ✅ present (new) | low |  |
| `closeFsModal` (onclick) | fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L2910 | ✅ present (new) | low |  |
| `compModal` (id) | bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompact-2b2e69850cfd4eef.jsonl:L55 | ✅ present | low |  |
| `drillModal` (id) | bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompact-2b2e69850cfd4eef.jsonl:L55 | ✅ present | low |  |
| `fsModal` (id) | fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L2910 | ✅ present (new) | low |  |
| `glossaryModal` (id) | f168094b-9d6e-466e-ba15-6b0f8cbc7c6e.jsonl:L322 | ✅ present (new) | low |  |
| `groupModal` (id) | bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompact-2b2e69850cfd4eef.jsonl:L55 | ✅ present | low |  |
| `kbdHelpModal` (id) | f168094b-9d6e-466e-ba15-6b0f8cbc7c6e.jsonl:L269 | ✅ present (new) | low |  |
| `metricModal` (id) | bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompact-2b2e69850cfd4eef.jsonl:L55 | ✅ present | low |  |
| `reportModal` (id) | bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompact-2b2e69850cfd4eef.jsonl:L55 | ✅ present | low |  |
| `stockModal` (id) | bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompact-2b2e69850cfd4eef.jsonl:L55 | ✅ present | low |  |
| `unownedModal` (id) | bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompact-2b2e69850cfd4eef.jsonl:L55 | ✅ present | low |  |

### popover

| Feature | Source(s) | Status | Priority | Notes |
|---|---|---|---|---|
| `openRbePopover` (onclick) | bf250eb0-8cb6-4c32-96f7-d26d443c8a97.jsonl:L342, fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L725, fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L728 (×4) | ❌ missing | medium |  |
| `rbePopover` (id) | 0306b5a0-0173-4ce1-8e03-64e3cca07936.jsonl:L717, bf250eb0-8cb6-4c32-96f7-d26d443c8a97.jsonl:L336, fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L1101 (×4) | ❌ missing | medium |  |
| `openRbePopover` (function) | bf250eb0-8cb6-4c32-96f7-d26d443c8a97.jsonl:L339 | ❌ missing | low |  |
| `showCashPopover` (function) | 0306b5a0-0173-4ce1-8e03-64e3cca07936.jsonl:L467 | ❌ missing | low |  |
| `showCashPopover` (onclick) | 0306b5a0-0173-4ce1-8e03-64e3cca07936.jsonl:L470 | ❌ missing | low |  |

### radar

| Feature | Source(s) | Status | Priority | Notes |
|---|---|---|---|---|
| `compRadarDiv` (id) | 6790f467-65e5-4043-923d-14cd2da4c529.jsonl:L1384, 6790f467-65e5-4043-923d-14cd2da4c529/subagents/agent-acompact-51ea98d896d5f5d7.jsonl:L238, 9bb62f73-0e91-4b88-8263-95e8523b2238.jsonl:L1203 (×5) | ✅ present | medium |  |
| `Risk Radar` (card-title) | 6790f467-65e5-4043-923d-14cd2da4c529.jsonl:L1384, 6790f467-65e5-4043-923d-14cd2da4c529/subagents/agent-acompact-51ea98d896d5f5d7.jsonl:L238, 9bb62f73-0e91-4b88-8263-95e8523b2238.jsonl:L1203 (×4) | ✅ present | medium |  |
| `Score Radar (Q1 = best, outer ring)` (card-title) | 9bb62f73-0e91-4b88-8263-95e8523b2238.jsonl:L875, 9bb62f73-0e91-4b88-8263-95e8523b2238/subagents/agent-acompact-f59e4390ac8d39a6.jsonl:L228 (×2) | ✅ present (new) | medium |  |
| `cmpRow` (function) | fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L2024 | ❌ missing | low |  |
| `Radar Comparison` (card-title) | bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompact-2b2e69850cfd4eef.jsonl:L107 | ❌ missing | low |  |
| `Score Radar` (card-title) | bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompact-2b2e69850cfd4eef.jsonl:L131 | ✅ present | low |  |
| `stockRadarDiv` (id) | 9bb62f73-0e91-4b88-8263-95e8523b2238.jsonl:L875, 9bb62f73-0e91-4b88-8263-95e8523b2238/subagents/agent-acompact-f59e4390ac8d39a6.jsonl:L228, bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompac… (×3) | ✅ present | low |  |

### region

| Feature | Source(s) | Status | Priority | Notes |
|---|---|---|---|---|
| Region disclaimer when coverage < 50% | CLAUDE.md Features | ❌ missing | medium |  |
| `toggleRegView` (onclick) | 875a1df5-d045-4fed-bd15-774cf1ce2337.jsonl:L145, 875a1df5-d045-4fed-bd15-774cf1ce2337/subagents/agent-acompact-36cc92af1a191d24.jsonl:L135, bf250eb0-8cb6-4c32-96f7-d26d443c8a97.jsonl:L1202 (×4) | ✅ present | medium |  |
| Region Active Weights (cardRegions) | TILE_SPEC.md Tier 3 #17 | ✅ present | medium |  |
| `regBenchSparkline` (function) | bf250eb0-8cb6-4c32-96f7-d26d443c8a97.jsonl:L1184 | ❌ missing | low |  |
| `regChart2` (id) | 0f6b5a8f-d645-4fb2-8123-64f4d239f8ce.jsonl:L128, 0f6b5a8f-d645-4fb2-8123-64f4d239f8ce/subagents/agent-acompact-840fe4766c4084ee.jsonl:L97 (×2) | ❌ missing | low |  |
| `regChartDiv2` (id) | 0f6b5a8f-d645-4fb2-8123-64f4d239f8ce.jsonl:L128, 0f6b5a8f-d645-4fb2-8123-64f4d239f8ce/subagents/agent-acompact-840fe4766c4084ee.jsonl:L97 (×2) | ❌ missing | low |  |
| `regRankAvg` (id) | fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L741 | ❌ missing | low |  |
| `regRankBM` (id) | fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L741 | ❌ missing | low |  |
| `regRankPort` (id) | fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L741 | ❌ missing | low |  |
| `regRankWtd` (id) | fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L741 | ❌ missing | low |  |
| `regSpark_13` (id) | bf250eb0-8cb6-4c32-96f7-d26d443c8a97.jsonl:L1202 | ❌ missing | low |  |
| `regSpark_2` (id) | bf250eb0-8cb6-4c32-96f7-d26d443c8a97.jsonl:L1202 | ❌ missing | low |  |
| `regSpark_4` (id) | bf250eb0-8cb6-4c32-96f7-d26d443c8a97.jsonl:L1202 | ❌ missing | low |  |
| `regSpark_6` (id) | bf250eb0-8cb6-4c32-96f7-d26d443c8a97.jsonl:L1202 | ❌ missing | low |  |
| `regSparkline` (function) | bf250eb0-8cb6-4c32-96f7-d26d443c8a97.jsonl:L1184 | ❌ missing | low |  |
| `regTable2` (id) | 0f6b5a8f-d645-4fb2-8123-64f4d239f8ce.jsonl:L128, 0f6b5a8f-d645-4fb2-8123-64f4d239f8ce/subagents/agent-acompact-840fe4766c4084ee.jsonl:L97 (×2) | ❌ missing | low |  |
| `setRegSparkWin` (function) | bf250eb0-8cb6-4c32-96f7-d26d443c8a97.jsonl:L1188 | ❌ missing | low |  |
| `setRegSparkWin` (onclick) | bf250eb0-8cb6-4c32-96f7-d26d443c8a97.jsonl:L1202 | ❌ missing | low |  |
| `toggleRegView2` (function) | 0f6b5a8f-d645-4fb2-8123-64f4d239f8ce.jsonl:L184 | ❌ missing | low |  |
| `toggleRegView2` (onclick) | 0f6b5a8f-d645-4fb2-8123-64f4d239f8ce.jsonl:L128, 0f6b5a8f-d645-4fb2-8123-64f4d239f8ce/subagents/agent-acompact-840fe4766c4084ee.jsonl:L97 (×2) | ❌ missing | low |  |
| `regChart` (id) | 875a1df5-d045-4fed-bd15-774cf1ce2337.jsonl:L145, 875a1df5-d045-4fed-bd15-774cf1ce2337/subagents/agent-acompact-36cc92af1a191d24.jsonl:L135, bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompac… (×3) | ✅ present | low |  |
| `regChartDiv` (id) | 875a1df5-d045-4fed-bd15-774cf1ce2337.jsonl:L145, 875a1df5-d045-4fed-bd15-774cf1ce2337/subagents/agent-acompact-36cc92af1a191d24.jsonl:L135, bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompac… (×3) | ✅ present | low |  |
| `regTable` (id) | 875a1df5-d045-4fed-bd15-774cf1ce2337.jsonl:L145, 875a1df5-d045-4fed-bd15-774cf1ce2337/subagents/agent-acompact-36cc92af1a191d24.jsonl:L135, bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompac… (×3) | ✅ present | low |  |
| `rRegChart` (function) | fbae49d0-369a-42ae-8bee-3fbd440690f7.jsonl:L388 | ✅ present | low |  |

### risk-decomp

| Feature | Source(s) | Status | Priority | Notes |
|---|---|---|---|---|
| MCR Top 10 (cardMCR) | TILE_SPEC.md Tier 2 #10 | ✅ present | high |  |
| TE Stacked Area hero (Risk) | TILE_SPEC.md Tier 2 #7 | 🤷 unclear | high |  |
| Risk Decomposition Tree (premium) | cli-prompts/risk-decomposition-tree-patch.md | ✅ present | medium |  |
| Unowned Risk Contributors (cardUnowned) | TILE_SPEC.md Tier 5 #24 | ✅ present | medium |  |
| `riskDecompDiv` (id) | 6790f467-65e5-4043-923d-14cd2da4c529.jsonl:L1416, 6790f467-65e5-4043-923d-14cd2da4c529/subagents/agent-acompact-51ea98d896d5f5d7.jsonl:L265 (×2) | ❌ missing | low |  |
| `riskDecompTree` (function) | f168094b-9d6e-466e-ba15-6b0f8cbc7c6e.jsonl:L224 | ✅ present (new) | low |  |

### scatter

| Feature | Source(s) | Status | Priority | Notes |
|---|---|---|---|---|
| `Risk/Return Scatter` (card-title) | bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompact-2b2e69850cfd4eef.jsonl:L182, fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L2965, risk-return-scatter-spec.md:L69 (×3) | ❌ missing (regressed) | high |  |
| `scatSecColor` (function) | risk-return-scatter-spec.md:L102, risk-return-scatter-spec.md:L112, risk-return-scatter-spec.md:L72 (×5) | ❌ missing | medium |  |
| `setScatMode` (function) | risk-return-scatter-spec.md:L102, risk-return-scatter-spec.md:L112, risk-return-scatter-spec.md:L72 (×5) | ❌ missing | medium |  |
| `rScat` (function) | risk-return-scatter-spec.md:L102, risk-return-scatter-spec.md:L112, risk-return-scatter-spec.md:L72 (×5) | ✅ present | medium |  |
| Risk/Return Scatter (cardScatter) | TILE_SPEC.md Tier 5 #22; tile-specs/risk-return-scatter-spec.md | ✅ present | medium |  |
| `corrScatterDiv` (id) | bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompact-2b2e69850cfd4eef.jsonl:L59 | ❌ missing (regressed) | low |  |
| `setScatMode` (onclick) | 0306b5a0-0173-4ce1-8e03-64e3cca07936.jsonl:L116, risk-return-scatter-spec.md:L69 (×2) | ❌ missing | low |  |
| `_fsScat_selectHold` (onclick) | fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L2929 | ✅ present (new) | low |  |
| `cardScatter` (id) | bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompact-2b2e69850cfd4eef.jsonl:L182, risk-return-scatter-spec.md:L69 (×2) | ✅ present | low |  |
| `fsScatDetail` (id) | fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L2929 | ✅ present (new) | low |  |
| `fsScatTable` (id) | fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L2929 | ✅ present (new) | low |  |
| `renderFsScatter` (function) | fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L2929 | ✅ present (new) | low |  |
| `scatDiv` (id) | bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompact-2b2e69850cfd4eef.jsonl:L182, risk-return-scatter-spec.md:L69 (×2) | ✅ present | low |  |

### sector

| Feature | Source(s) | Status | Priority | Notes |
|---|---|---|---|---|
| `Sector Active Weight Heatmap (all strategies)` (card-title) | 6790f467-65e5-4043-923d-14cd2da4c529.jsonl:L1384, 6790f467-65e5-4043-923d-14cd2da4c529/subagents/agent-acompact-51ea98d896d5f5d7.jsonl:L238 (×2) | ❌ missing (regressed) | high |  |
| `toggleScatSector` (function) | risk-return-scatter-spec.md:L102, risk-return-scatter-spec.md:L112, risk-return-scatter-spec.md:L72 (×5) | ❌ missing | high |  |
| `Sector Active Weights` (card-title) | 0306b5a0-0173-4ce1-8e03-64e3cca07936.jsonl:L1906, 875a1df5-d045-4fed-bd15-774cf1ce2337.jsonl:L135, 875a1df5-d045-4fed-bd15-774cf1ce2337/subagents/agent-acompact-36cc92af1a191d24.jsonl:L128 (×5) | ✅ present | high |  |
| Sector Active Weights (cardSectors) | TILE_SPEC.md Tier 1 #6; tile-specs/sector-active-weights-spec.md | ✅ present | high |  |
| `Brinson Attribution (Sector-Based)` (card-title) | bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompact-2b2e69850cfd4eef.jsonl:L204 | ❌ missing (regressed) | medium |  |
| `Factor Contributions to Sector TE` (card-title) | bf250eb0-8cb6-4c32-96f7-d26d443c8a97.jsonl:L158 | ❌ missing | medium |  |
| `Per-Sector Impact Detail` (card-title) | bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompact-2b2e69850cfd4eef.jsonl:L59 | ❌ missing (regressed) | medium |  |
| `secBenchSparkline` (function) | bf250eb0-8cb6-4c32-96f7-d26d443c8a97.jsonl:L932, bf250eb0-8cb6-4c32-96f7-d26d443c8a97/subagents/agent-ad34f454afdb0c094.jsonl:L54, bf250eb0-8cb6-4c32-96f7-d26d443c8a97/subagents/agent-ad34f454afdb0c09… (×3) | ❌ missing | medium |  |
| `Sector Allocation` (card-title) | 0f6b5a8f-d645-4fb2-8123-64f4d239f8ce.jsonl:L117, 0f6b5a8f-d645-4fb2-8123-64f4d239f8ce/subagents/agent-acompact-840fe4766c4084ee.jsonl:L89 (×2) | ❌ missing | medium |  |
| `Sector Detail — sorted by TE Contribution` (card-title) | 0f6b5a8f-d645-4fb2-8123-64f4d239f8ce.jsonl:L117, 0f6b5a8f-d645-4fb2-8123-64f4d239f8ce/subagents/agent-acompact-840fe4766c4084ee.jsonl:L89 (×2) | ❌ missing | medium |  |
| `toggleSectorGroup` (onclick) | 0306b5a0-0173-4ce1-8e03-64e3cca07936.jsonl:L804, fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L1997, fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L2003 (×3) | ❌ missing | medium |  |
| Sector heatmap comparison across all 7 strategies | CLAUDE.md Features | ❌ missing | medium |  |
| `cardSectors` (id) | 875a1df5-d045-4fed-bd15-774cf1ce2337.jsonl:L135, 875a1df5-d045-4fed-bd15-774cf1ce2337/subagents/agent-acompact-36cc92af1a191d24.jsonl:L128, bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompac… (×3) | ✅ present | medium |  |
| `parseCSVLine` (function) | 37b9aba8-d807-4adf-b672-764e27067d0e.jsonl:L100, 9bb62f73-0e91-4b88-8263-95e8523b2238.jsonl:L135, 9bb62f73-0e91-4b88-8263-95e8523b2238/subagents/agent-acompact-5d03aa71ce7b3960.jsonl:L134 (×4) | ✅ present | medium |  |
| `Sector Active Weight Heatmap` (card-title) | 9bb62f73-0e91-4b88-8263-95e8523b2238.jsonl:L1203, 9bb62f73-0e91-4b88-8263-95e8523b2238/subagents/agent-acompact-278d4915e57367f7.jsonl:L255 (×2) | ✅ present | medium |  |
| `toggleSecView` (onclick) | 875a1df5-d045-4fed-bd15-774cf1ce2337.jsonl:L135, 875a1df5-d045-4fed-bd15-774cf1ce2337/subagents/agent-acompact-36cc92af1a191d24.jsonl:L128, bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompac… (×3) | ✅ present | medium |  |
| `bmGapDiv` (id) | fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L520 | ❌ missing | low |  |
| `bmSecDiv` (id) | fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L316, fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L520 (×2) | ❌ missing | low |  |
| `rSecChartButterfly` (function) | sector-active-weights-spec.md:L134 | ❌ missing | low |  |
| `rSecChartTreemap` (function) | sector-active-weights-spec.md:L134 | ❌ missing | low |  |
| `rSecChartWaterfall` (function) | bf250eb0-8cb6-4c32-96f7-d26d443c8a97.jsonl:L141, sector-active-weights-spec.md:L134 (×2) | ❌ missing | low |  |
| `rSectors` (function) | 0f6b5a8f-d645-4fb2-8123-64f4d239f8ce.jsonl:L117, 0f6b5a8f-d645-4fb2-8123-64f4d239f8ce/subagents/agent-acompact-840fe4766c4084ee.jsonl:L89 (×2) | ❌ missing | low |  |
| `rSecTreemap` (function) | 0f6b5a8f-d645-4fb2-8123-64f4d239f8ce.jsonl:L117, 0f6b5a8f-d645-4fb2-8123-64f4d239f8ce/subagents/agent-acompact-840fe4766c4084ee.jsonl:L89 (×2) | ❌ missing | low |  |
| `scatSectorBtn` (id) | risk-return-scatter-spec.md:L69 | ❌ missing | low |  |
| `secFacWatDiv` (id) | 0f6b5a8f-d645-4fb2-8123-64f4d239f8ce.jsonl:L117, 0f6b5a8f-d645-4fb2-8123-64f4d239f8ce/subagents/agent-acompact-840fe4766c4084ee.jsonl:L89 (×2) | ❌ missing | low |  |
| `secSpark_13` (id) | bf250eb0-8cb6-4c32-96f7-d26d443c8a97/subagents/agent-ad34f454afdb0c094.jsonl:L70 | ❌ missing | low |  |
| `secSpark_2` (id) | bf250eb0-8cb6-4c32-96f7-d26d443c8a97/subagents/agent-ad34f454afdb0c094.jsonl:L70 | ❌ missing | low |  |
| `secSpark_4` (id) | bf250eb0-8cb6-4c32-96f7-d26d443c8a97/subagents/agent-ad34f454afdb0c094.jsonl:L70 | ❌ missing | low |  |
| `secSpark_6` (id) | bf250eb0-8cb6-4c32-96f7-d26d443c8a97/subagents/agent-ad34f454afdb0c094.jsonl:L70 | ❌ missing | low |  |
| `secSparkline` (function) | 0306b5a0-0173-4ce1-8e03-64e3cca07936.jsonl:L452, bf250eb0-8cb6-4c32-96f7-d26d443c8a97/subagents/agent-ad34f454afdb0c094.jsonl:L51 (×2) | ❌ missing | low |  |
| `Sector Active Weight Diff (${keys[0]} − ${keys[1]})` (card-title) | bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompact-2b2e69850cfd4eef.jsonl:L107 | ❌ missing | low |  |
| `secTreemapDiv` (id) | 0f6b5a8f-d645-4fb2-8123-64f4d239f8ce.jsonl:L117, 0f6b5a8f-d645-4fb2-8123-64f4d239f8ce/subagents/agent-acompact-840fe4766c4084ee.jsonl:L89 (×2) | ❌ missing | low |  |
| `setSecRankSrc` (function) | 0306b5a0-0173-4ce1-8e03-64e3cca07936.jsonl:L408, bf250eb0-8cb6-4c32-96f7-d26d443c8a97/subagents/agent-ad34f454afdb0c094.jsonl:L48 (×2) | ❌ missing | low |  |
| `setSecSparkWin` (function) | bf250eb0-8cb6-4c32-96f7-d26d443c8a97/subagents/agent-ad34f454afdb0c094.jsonl:L48 | ❌ missing | low |  |
| `setSecSparkWin` (onclick) | bf250eb0-8cb6-4c32-96f7-d26d443c8a97/subagents/agent-ad34f454afdb0c094.jsonl:L70 | ❌ missing | low |  |
| `setSectorFilter` (onclick) | bf250eb0-8cb6-4c32-96f7-d26d443c8a97.jsonl:L1484 | ❌ missing | low |  |
| `switchSecChart` (function) | 0306b5a0-0173-4ce1-8e03-64e3cca07936.jsonl:L442, sector-active-weights-spec.md:L134 (×2) | ❌ missing | low |  |
| `switchSecChart` (onclick) | sector-active-weights-spec.md:L126 | ❌ missing | low |  |
| `tab-sectors` (id) | 0f6b5a8f-d645-4fb2-8123-64f4d239f8ce.jsonl:L68, 0f6b5a8f-d645-4fb2-8123-64f4d239f8ce/subagents/agent-acompact-840fe4766c4084ee.jsonl:L54 (×2) | ❌ missing | low |  |
| `toggleScatSector` (onclick) | risk-return-scatter-spec.md:L69 | ❌ missing | low |  |
| `toggleSecRow` (function) | 0f6b5a8f-d645-4fb2-8123-64f4d239f8ce.jsonl:L117, 0f6b5a8f-d645-4fb2-8123-64f4d239f8ce/subagents/agent-acompact-840fe4766c4084ee.jsonl:L89 (×2) | ❌ missing | low |  |
| `toggleSectorGroup` (function) | 0306b5a0-0173-4ce1-8e03-64e3cca07936.jsonl:L787 | ❌ missing | low |  |
| `Compare to Other ${type==='sec'?'Sectors':'Regions'}` (card-title) | bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompact-2b2e69850cfd4eef.jsonl:L103 | ✅ present | low |  |
| `rSecChart` (function) | sector-active-weights-spec.md:L134 | ✅ present | low |  |
| `secRankAvg` (id) | bf250eb0-8cb6-4c32-96f7-d26d443c8a97.jsonl:L104, bf250eb0-8cb6-4c32-96f7-d26d443c8a97.jsonl:L108, bf250eb0-8cb6-4c32-96f7-d26d443c8a97.jsonl:L129 (×3) | ✅ present (new) | low |  |
| `secRankToggleHtml` (function) | 0306b5a0-0173-4ce1-8e03-64e3cca07936.jsonl:L415, fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L722 (×2) | ✅ present (new) | low |  |
| `secRankWtd` (id) | bf250eb0-8cb6-4c32-96f7-d26d443c8a97.jsonl:L104, bf250eb0-8cb6-4c32-96f7-d26d443c8a97.jsonl:L108, bf250eb0-8cb6-4c32-96f7-d26d443c8a97.jsonl:L129 (×3) | ✅ present (new) | low |  |
| `toggleSecView` (function) | 0306b5a0-0173-4ce1-8e03-64e3cca07936.jsonl:L445 | ✅ present | low |  |

### settings-prefs

| Feature | Source(s) | Status | Priority | Notes |
|---|---|---|---|---|
| `rr_hold_cols` (localStorage) | holdings-tab-spec.md:L48, holdings-tab-spec.md:L58, holdings-tab-spec.md:L68 (×3) | ❌ missing | medium |  |
| `rr_hold_prefs_` (localStorage) | 0306b5a0-0173-4ce1-8e03-64e3cca07936.jsonl:L1670, 0306b5a0-0173-4ce1-8e03-64e3cca07936.jsonl:L1675, 0306b5a0-0173-4ce1-8e03-64e3cca07936.jsonl:L1678 (×5) | ❌ missing | medium |  |
| `applyPrefs` (function) | 9bb62f73-0e91-4b88-8263-95e8523b2238.jsonl:L1218, 9bb62f73-0e91-4b88-8263-95e8523b2238/subagents/agent-acompact-278d4915e57367f7.jsonl:L270, fbae49d0-369a-42ae-8bee-3fbd440690f7.jsonl:L386 (×3) | ✅ present (new) | medium |  |
| `facThreshSlider` (id) | 0f6b5a8f-d645-4fb2-8123-64f4d239f8ce.jsonl:L128, 0f6b5a8f-d645-4fb2-8123-64f4d239f8ce/subagents/agent-acompact-840fe4766c4084ee.jsonl:L97, 9bb62f73-0e91-4b88-8263-95e8523b2238.jsonl:L879 (×8) | ✅ present (new) | medium |  |
| `facThreshVal` (id) | 0f6b5a8f-d645-4fb2-8123-64f4d239f8ce.jsonl:L128, 0f6b5a8f-d645-4fb2-8123-64f4d239f8ce/subagents/agent-acompact-840fe4766c4084ee.jsonl:L97, 9bb62f73-0e91-4b88-8263-95e8523b2238.jsonl:L879 (×8) | ✅ present (new) | medium |  |
| `populatePrefPanel` (function) | 0306b5a0-0173-4ce1-8e03-64e3cca07936.jsonl:L2448, 9bb62f73-0e91-4b88-8263-95e8523b2238.jsonl:L1218, 9bb62f73-0e91-4b88-8263-95e8523b2238/subagents/agent-acompact-278d4915e57367f7.jsonl:L270 (×3) | ✅ present (new) | medium |  |
| `savePref` (function) | 529c73ed-d7c3-4965-8e2a-33f7fef38298.jsonl:L42, 9bb62f73-0e91-4b88-8263-95e8523b2238.jsonl:L1218, 9bb62f73-0e91-4b88-8263-95e8523b2238/subagents/agent-acompact-278d4915e57367f7.jsonl:L270 (×3) | ✅ present (new) | medium |  |
| `setFacThresh` (function) | 9bb62f73-0e91-4b88-8263-95e8523b2238.jsonl:L894, 9bb62f73-0e91-4b88-8263-95e8523b2238/subagents/agent-acompact-f59e4390ac8d39a6.jsonl:L247, b2861e29-fdab-4386-a79d-886c89059725.jsonl:L779 (×6) | ✅ present (new) | medium |  |
| Theme System + Accessibility | cli-prompts/theme-accessibility-patch.md | ✅ present | medium |  |
| `rr_sec_chart_mode` (localStorage) | 0306b5a0-0173-4ce1-8e03-64e3cca07936.jsonl:L440, 0306b5a0-0173-4ce1-8e03-64e3cca07936.jsonl:L442 (×2) | ❌ missing | low |  |
| `rr_sec_sort` (localStorage) | 0306b5a0-0173-4ce1-8e03-64e3cca07936.jsonl:L401, 0306b5a0-0173-4ce1-8e03-64e3cca07936.jsonl:L403 (×2) | ❌ missing | low |  |
| `loadPrefs` (function) | 9bb62f73-0e91-4b88-8263-95e8523b2238.jsonl:L1218, 9bb62f73-0e91-4b88-8263-95e8523b2238/subagents/agent-acompact-278d4915e57367f7.jsonl:L270 (×2) | ✅ present (new) | low |  |
| `prefDefaultStrat` (id) | 9bb62f73-0e91-4b88-8263-95e8523b2238.jsonl:L1184, 9bb62f73-0e91-4b88-8263-95e8523b2238/subagents/agent-acompact-278d4915e57367f7.jsonl:L236 (×2) | ✅ present (new) | low |  |
| `prefPinnedWrap` (id) | 9bb62f73-0e91-4b88-8263-95e8523b2238.jsonl:L1184, 9bb62f73-0e91-4b88-8263-95e8523b2238/subagents/agent-acompact-278d4915e57367f7.jsonl:L236 (×2) | ✅ present (new) | low |  |
| `rr_config` (localStorage) | bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompact-2b2e69850cfd4eef.jsonl:L212, bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompact-2b2e69850cfd4eef.jsonl:L59 (×2) | ✅ present | low |  |
| `rr_flags_` (localStorage) | fbae49d0-369a-42ae-8bee-3fbd440690f7.jsonl:L826, fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L2993 (×2) | ✅ present (new) | low |  |
| `rr_holdsnap_v1` (localStorage) | fbae49d0-369a-42ae-8bee-3fbd440690f7.jsonl:L1170 | ✅ present (new) | low |  |
| `savePrefs` (function) | 9bb62f73-0e91-4b88-8263-95e8523b2238.jsonl:L1218, 9bb62f73-0e91-4b88-8263-95e8523b2238/subagents/agent-acompact-278d4915e57367f7.jsonl:L270 (×2) | ✅ present (new) | low |  |
| `setPrecisionPref` (function) | 9bb62f73-0e91-4b88-8263-95e8523b2238.jsonl:L1218, 9bb62f73-0e91-4b88-8263-95e8523b2238/subagents/agent-acompact-278d4915e57367f7.jsonl:L270 (×2) | ✅ present (new) | low |  |
| `setPrecisionPref` (onclick) | 9bb62f73-0e91-4b88-8263-95e8523b2238.jsonl:L1184, 9bb62f73-0e91-4b88-8263-95e8523b2238/subagents/agent-acompact-278d4915e57367f7.jsonl:L236 (×2) | ✅ present (new) | low |  |
| `setThemePref` (function) | 9bb62f73-0e91-4b88-8263-95e8523b2238.jsonl:L1218, 9bb62f73-0e91-4b88-8263-95e8523b2238/subagents/agent-acompact-278d4915e57367f7.jsonl:L270 (×2) | ✅ present (new) | low |  |
| `setThemePref` (onclick) | 9bb62f73-0e91-4b88-8263-95e8523b2238.jsonl:L1184, 9bb62f73-0e91-4b88-8263-95e8523b2238/subagents/agent-acompact-278d4915e57367f7.jsonl:L236 (×2) | ✅ present (new) | low |  |
| `THEME` (function) | fbae49d0-369a-42ae-8bee-3fbd440690f7.jsonl:L379, fbae49d0-369a-42ae-8bee-3fbd440690f7.jsonl:L482 (×2) | ✅ present (new) | low |  |
| `themeDark` (id) | 9bb62f73-0e91-4b88-8263-95e8523b2238.jsonl:L1184, 9bb62f73-0e91-4b88-8263-95e8523b2238/subagents/agent-acompact-278d4915e57367f7.jsonl:L236 (×2) | ✅ present (new) | low |  |
| `themeLight` (id) | 9bb62f73-0e91-4b88-8263-95e8523b2238.jsonl:L1184, 9bb62f73-0e91-4b88-8263-95e8523b2238/subagents/agent-acompact-278d4915e57367f7.jsonl:L236 (×2) | ✅ present (new) | low |  |

### sparkline

| Feature | Source(s) | Status | Priority | Notes |
|---|---|---|---|---|
| Factor exposure sparklines (inline SVG) | CLAUDE.md Features | ❌ missing | medium |  |
| `mkStackedSparkline` (function) | bf250eb0-8cb6-4c32-96f7-d26d443c8a97.jsonl:L1326 | ❌ missing | low |  |
| `mkSparkline` (function) | 6790f467-65e5-4043-923d-14cd2da4c529.jsonl:L1430, 6790f467-65e5-4043-923d-14cd2da4c529/subagents/agent-acompact-51ea98d896d5f5d7.jsonl:L276 (×2) | ✅ present | low |  |

### stress

| Feature | Source(s) | Status | Priority | Notes |
|---|---|---|---|---|
| `oDrStress` (onclick) | bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompact-2b2e69850cfd4eef.jsonl:L75 | ❌ missing (regressed) | medium |  |
| `Stress Scenarios` (card-title) | bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompact-2b2e69850cfd4eef.jsonl:L182 | ❌ missing (regressed) | medium |  |
| `stressModal` (id) | bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompact-2b2e69850cfd4eef.jsonl:L55 | ❌ missing (regressed) | medium |  |
| `cardStress` (id) | bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompact-2b2e69850cfd4eef.jsonl:L182 | ❌ missing (regressed) | low |  |
| `oDrStress` (function) | bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompact-2b2e69850cfd4eef.jsonl:L59 | ❌ missing (regressed) | low |  |
| `rStressTable` (function) | bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompact-2b2e69850cfd4eef.jsonl:L75 | ❌ missing (regressed) | low |  |
| `stressContent` (id) | bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompact-2b2e69850cfd4eef.jsonl:L55 | ❌ missing (regressed) | low |  |
| `stressWaterfallDiv` (id) | bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompact-2b2e69850cfd4eef.jsonl:L59 | ❌ missing (regressed) | low |  |

### thresholds-alerts

| Feature | Source(s) | Status | Priority | Notes |
|---|---|---|---|---|
| Risk Alerts Banner — Anomaly Detection | cli-prompts/risk-alerts-patch.md | ✅ present | high |  |
| `resetThresholds` (onclick) | 0306b5a0-0173-4ce1-8e03-64e3cca07936.jsonl:L2441, 529c73ed-d7c3-4965-8e2a-33f7fef38298.jsonl:L63, fbae49d0-369a-42ae-8bee-3fbd440690f7.jsonl:L672 (×3) | ✅ present (new) | medium |  |
| `setThreshold` (function) | 0306b5a0-0173-4ce1-8e03-64e3cca07936.jsonl:L2434, 529c73ed-d7c3-4965-8e2a-33f7fef38298.jsonl:L42, fbae49d0-369a-42ae-8bee-3fbd440690f7.jsonl:L676 (×3) | ✅ present (new) | medium |  |
| Watchlist + Threshold Alerts | cli-prompts/watchlist-alerts-patch.md | ✅ present | medium |  |
| `thrAsMin` (id) | 0306b5a0-0173-4ce1-8e03-64e3cca07936.jsonl:L2441 | ❌ missing | low |  |
| `thrCashMax` (id) | 0306b5a0-0173-4ce1-8e03-64e3cca07936.jsonl:L2441 | ❌ missing | low |  |
| `Threshold Breaches (${breaches.length})` (card-title) | bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompact-2b2e69850cfd4eef.jsonl:L59 | ❌ missing | low |  |
| `Threshold Events (${breaches.length})` (card-title) | bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompact-2b2e69850cfd4eef.jsonl:L294 | ❌ missing | low |  |
| `thrQ5Max` (id) | 0306b5a0-0173-4ce1-8e03-64e3cca07936.jsonl:L2441 | ❌ missing | low |  |
| `thrTeConc` (id) | 0306b5a0-0173-4ce1-8e03-64e3cca07936.jsonl:L2441 | ❌ missing | low |  |
| `thrTeCrit` (id) | 0306b5a0-0173-4ce1-8e03-64e3cca07936.jsonl:L2441 | ❌ missing | low |  |
| `thrTeWarn` (id) | 0306b5a0-0173-4ce1-8e03-64e3cca07936.jsonl:L2441 | ❌ missing | low |  |
| `loadThresholds` (function) | 529c73ed-d7c3-4965-8e2a-33f7fef38298.jsonl:L42 | ✅ present (new) | low |  |
| `resetThresholds` (function) | 0306b5a0-0173-4ce1-8e03-64e3cca07936.jsonl:L2434, 529c73ed-d7c3-4965-8e2a-33f7fef38298.jsonl:L42 (×2) | ✅ present (new) | low |  |
| `rr_thresholds` (localStorage) | 0306b5a0-0173-4ce1-8e03-64e3cca07936.jsonl:L2434 | ✅ present (new) | low |  |
| `saveThresholds` (function) | 0306b5a0-0173-4ce1-8e03-64e3cca07936.jsonl:L2434, 529c73ed-d7c3-4965-8e2a-33f7fef38298.jsonl:L42 (×2) | ✅ present (new) | low |  |
| `Threshold Events (${breaches.length} months)` (card-title) | bf720b9d-9e2c-41d7-a433-c3181388c137/subagents/agent-acompact-2b2e69850cfd4eef.jsonl:L316 | ✅ present | low |  |

### treemap

| Feature | Source(s) | Status | Priority | Notes |
|---|---|---|---|---|
| `setTreeColorMode` (onclick) | 0306b5a0-0173-4ce1-8e03-64e3cca07936.jsonl:L1165, 0306b5a0-0173-4ce1-8e03-64e3cca07936.jsonl:L1169, fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L1411 (×3) | ❌ missing | medium |  |
| `setTreeDim` (function) | 0306b5a0-0173-4ce1-8e03-64e3cca07936.jsonl:L1172, active-weight-treemap-spec.md:L116, active-weight-treemap-spec.md:L122 (×6) | ❌ missing | medium |  |
| `setTreeDim` (onclick) | active-weight-treemap-spec.md:L103, active-weight-treemap-spec.md:L95, fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L435 (×3) | ❌ missing | medium |  |
| `setTreeMode` (onclick) | 0306b5a0-0173-4ce1-8e03-64e3cca07936.jsonl:L1165, 0306b5a0-0173-4ce1-8e03-64e3cca07936.jsonl:L1169, fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L435 (×3) | ❌ missing | medium |  |
| `showTreeFacPanel` (function) | fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L106, fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L1259, fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L941 (×3) | ❌ missing | medium |  |
| `treeDrillBack` (function) | active-weight-treemap-spec.md:L116, active-weight-treemap-spec.md:L122, active-weight-treemap-spec.md:L134 (×6) | ❌ missing | medium |  |
| `treeDrillInto` (function) | 0306b5a0-0173-4ce1-8e03-64e3cca07936.jsonl:L1175, active-weight-treemap-spec.md:L116, active-weight-treemap-spec.md:L122 (×5) | ❌ missing | medium |  |
| Active Weight Treemap (cardTreemap) | TILE_SPEC.md Tier 5 #23; tile-specs/active-weight-treemap-spec.md | ✅ present | medium |  |
| `renderBmGapChart` (function) | fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L523 | ❌ missing | low |  |
| `renderBmOnlySection` (function) | fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L115 | ❌ missing | low |  |
| `renderBmSecChart` (function) | fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L316 | ❌ missing | low |  |
| `setTreeColorMode` (function) | 0306b5a0-0173-4ce1-8e03-64e3cca07936.jsonl:L1172 | ❌ missing | low |  |
| `setTreeMode` (function) | fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L439 | ❌ missing | low |  |
| `treeBreadcrumb` (id) | active-weight-treemap-spec.md:L103, active-weight-treemap-spec.md:L95 (×2) | ❌ missing | low |  |
| `treeColorA` (id) | 0306b5a0-0173-4ce1-8e03-64e3cca07936.jsonl:L1165, 0306b5a0-0173-4ce1-8e03-64e3cca07936.jsonl:L1169, fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L1411 (×3) | ❌ missing | low |  |
| `treeColorF` (id) | 0306b5a0-0173-4ce1-8e03-64e3cca07936.jsonl:L1165, 0306b5a0-0173-4ce1-8e03-64e3cca07936.jsonl:L1169, fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L1411 (×3) | ❌ missing | low |  |
| `treeColorQ` (id) | fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L1411 | ❌ missing | low |  |
| `treeDimCo` (id) | active-weight-treemap-spec.md:L103, active-weight-treemap-spec.md:L95, fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L435 (×3) | ❌ missing | low |  |
| `treeDimGrp` (id) | active-weight-treemap-spec.md:L103, active-weight-treemap-spec.md:L95, fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L435 (×3) | ❌ missing | low |  |
| `treeDimRank` (id) | active-weight-treemap-spec.md:L103, active-weight-treemap-spec.md:L95, fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L435 (×3) | ❌ missing | low |  |
| `treeDimSec` (id) | active-weight-treemap-spec.md:L103, active-weight-treemap-spec.md:L95, fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L435 (×3) | ❌ missing | low |  |
| `treeDrillBack` (onclick) | active-weight-treemap-spec.md:L103, active-weight-treemap-spec.md:L95 (×2) | ❌ missing | low |  |
| `treeFacPanel` (id) | fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L87 | ❌ missing | low |  |
| `treeModeF` (id) | 0306b5a0-0173-4ce1-8e03-64e3cca07936.jsonl:L1165, 0306b5a0-0173-4ce1-8e03-64e3cca07936.jsonl:L1169, fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L435 (×3) | ❌ missing | low |  |
| `treeModeP` (id) | 0306b5a0-0173-4ce1-8e03-64e3cca07936.jsonl:L1165, 0306b5a0-0173-4ce1-8e03-64e3cca07936.jsonl:L1169 (×2) | ❌ missing | low |  |
| `treeModeWt` (id) | 0306b5a0-0173-4ce1-8e03-64e3cca07936.jsonl:L1165, 0306b5a0-0173-4ce1-8e03-64e3cca07936.jsonl:L1169, fcdbea6c-f228-4db7-9d89-5f1010d47be5.jsonl:L435 (×3) | ❌ missing | low |  |

---

## Top 10 Missing by Priority

1. **`renderHoldCards` (function)** — ❌ missing · high priority · holdings-cards
2. **`toggleHoldExpand` (onclick)** — ❌ missing · high priority · holdings-cards
3. **`fillHoldCardsChunked` (function)** — ❌ missing · high priority · holdings-cards
4. **`toggleHoldExpand` (function)** — ❌ missing · high priority · holdings-cards
5. **`setHoldChip` (function)** — ❌ missing · high priority · holdings-cards
6. **`toggleScatSector` (function)** — ❌ missing · high priority · sector
7. **`Sector Concentration (Top 10 Holdings)` (card-title)** — ❌ missing (regressed) · high priority · holdings-general
8. **`Risk/Return Scatter` (card-title)** — ❌ missing (regressed) · high priority · scatter
9. **`Sector Active Weight Heatmap (all strategies)` (card-title)** — ❌ missing (regressed) · high priority · sector
10. **Email Report Generator** — ❌ missing · high priority · email-export
11. **Historical Trends mini-charts (TE, AS, Beta, Holdings)** — ❌ missing · high priority · mini-charts
12. **rHistoricalTrends mini-charts** — ❌ missing · high priority · mini-charts
13. **Summary Card — Factor Risk** — ❌ missing · high priority · mini-charts
14. **Historical week banner (amber) for past weeks** — ❌ missing · high priority · misc
15. **`renderOneCard` (function)** — ❌ missing · medium priority · misc

---

## Known Issues

- All 93 JSONL files parsed cleanly. No corrupt lines.

---

## Caveats

- Feature detection is string-based. A function may be renamed (e.g. `rFCorr` →
  `rUpdateCorr`) and appear missing when the logic is actually present under a new
  name. PM review should confirm.
- Card titles with template literals (`${name}`) are matched loosely.
- Helpers used exactly once (e.g. `cell`, `hex2rgba`) are kept in the table
  but marked low priority — they may be internal to a larger missing feature.
- Doc-derived patch features (`cli-prompts/*.md`) are proposed, not necessarily
  built; some may have been intentionally deferred. Status uses marker-string
  heuristics only — confirm with PM before treating as regressions.
