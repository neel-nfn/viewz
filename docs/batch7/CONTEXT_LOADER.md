# Context Loaded — Viewz (Batch-7 Completed · v0.7.0-beta)

**Built**: analytics v2 fields, /research/score API, Research UI, Chrome Extension MVP, scheduler rollups.

**Verified**: score pipeline (API→DB→UI), extension badge injection, RLS, non-zero velocity fields.

## Next Objectives

### 1) Scoring Model 7.1
- Add recency decay factor
- Implement keyword overlap detection
- Add competitor delta calculations

### 2) UX Polish
- Research table with sortable scores
- Save filters and search
- CSV export functionality

### 3) Extension Auth
- Org/channel picker + token storage
- Production API base URL configuration

### 4) Perf
- Snapshot indexing optimization
- Scheduler runtime budget monitoring

### 5) Public Docs
- Add Research section to /public/roadmap
- Update changelog with Batch-7 features

## Current State

- **Branch**: `feat/batch7-outlier` → merged to `main`
- **Tag**: `v0.7.0-beta`
- **Extension**: `release/viewz_outlier_extension_mv3.zip`
- **Docs**: `release/viewz_batch7_docs.zip`

## QA Acceptance Criteria (All Passed)

- ✅ `POST /api/v1/research/score` returns 200 with valid score & components
- ✅ Latest `analytics_snapshots` row shows updated v2 fields after scheduler run
- ✅ ResearchPage shows Outlier badge and components JSON
- ✅ Extension renders badge on YT watch pages
- ✅ Cross-org read/write blocked per RLS

