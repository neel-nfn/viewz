# Batch-7 Completion (Outlier Engine)

## Overview
Implementation completed for Topic Research & Outlier Engine with analytics v2 fields, scoring API, Research UI, Chrome Extension MVP, and scheduler rollups.

## Components Delivered

### 1. Analytics v2 Fields
- **Migration**: `004_analytics_v2_research.sql`
- **Fields Added**: 
  - `views_7d`, `views_28d` (rolling sums)
  - `ctr_7d`, `ctr_28d` (rolling averages)
  - `views_velocity_7d`, `views_velocity_28d` (growth rates)
  - `ctr_delta_7d`, `ctr_delta_28d` (CTR deltas)
  - `variance_7d` (variance for outlier detection)
- **Index**: Added `idx_analytics_snapshots_channel_date` for performance

### 2. Research Tables
- **research_ideas**: Stores research ideas from extension/UI/manual entry
- **research_scores**: Stores computed scores with component breakdown
- **RLS**: Policies configured for org-scoped access

### 3. Backend API
- **Endpoint**: `POST /api/v1/research/score`
- **Service**: `research_service.py` with outlier component computation
- **Schemas**: `ScoreIdeaRequest`, `ScoreResponse`
- **Scoring Logic**: Weighted components (views_velocity 50%, ctr_z 35%, freshness 15%)

### 4. Frontend Research UI
- **Page**: `/app/research` - ResearchPage component
- **Badge**: OutlierBadge with thresholds (🔥 Outlier ≥80, High ≥60, Medium ≥40, Low <40)
- **Service**: `researchService.js` with `scoreIdea()` function

### 5. Chrome Extension MVP
- **Manifest V3**: Configured with permissions
- **Content Script**: Extracts YouTube video title and injects badge
- **Background**: Calls API and sends score to content script
- **Popup**: Optional UI for manual scoring

### 6. Analytics Scheduler Integration
- **Service**: `analytics_rollup.py` computes v2 fields from snapshots
- **Integration**: Scheduler calls `rollup_all_channels()` each cycle
- **Computation**: Velocity, CTR deltas, variance calculations

## Files Created (17 total)

**Backend:**
- `backend/migrations/004_analytics_v2_research.sql`
- `backend/app/schemas/research_schemas.py`
- `backend/app/services/research_service.py`
- `backend/app/services/analytics_rollup.py`
- `backend/app/api/research.py`
- `backend/app/api/deps.py` (updated)

**Frontend:**
- `frontend/src/pages/Research/ResearchPage.jsx`
- `frontend/src/components/OutlierBadge.jsx`
- `frontend/src/services/researchService.js`
- `frontend/src/router/AppRouter.jsx` (updated)

**Extension:**
- `extension/manifest.json`
- `extension/content.js`
- `extension/background.js`
- `extension/popup.html`
- `extension/popup.js`

**Other:**
- `backend/app/main.py` (updated)
- `backend/app/services/scheduler.py` (updated)

## QA Checklist

- [x] API: `POST /api/v1/research/score` returns score 0–100 with components
- [x] DB: New rows present in `research_ideas` and `research_scores`
- [x] UI: Research page shows badge + components JSON
- [x] Extension: Badge appears on YouTube video pages
- [x] Scheduler: Analytics v2 fields populated on latest snapshots
- [x] RLS: Org-scoped access restrictions in place

## Next Steps (Batch-7.1)

1. **Scoring Model Enhancement**:
   - Add recency decay factor
   - Implement keyword overlap detection
   - Add competitor delta calculations

2. **UX Polish**:
   - Research table with sortable scores
   - Save filters and search
   - CSV export functionality

3. **Extension Auth**:
   - Org/channel picker
   - Token storage in extension
   - Production API base URL

4. **Performance**:
   - Snapshot indexing optimization
   - Scheduler runtime budget monitoring

5. **Documentation**:
   - Add Research section to public roadmap
   - Update changelog with Batch-7 features

## Version
**v0.7.0-beta** - Topic Research & Outlier Engine

