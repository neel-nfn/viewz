# Batch-7 QA Checklist

## API Testing
- [ ] `POST /api/v1/research/score` returns 200
- [ ] Response contains `score` (0-100) and `components` object
- [ ] Components include `views_velocity`, `ctr_z`, `freshness`

## Database Verification
- [ ] New row inserted in `research_ideas` table
- [ ] New row inserted in `research_scores` table
- [ ] `idea_id` matches between both tables
- [ ] RLS policies prevent cross-org access

## Frontend UI
- [ ] `/app/research` page loads correctly
- [ ] Can enter idea title and URL
- [ ] Clicking "Score" button shows result
- [ ] OutlierBadge displays correct label (🔥 Outlier/High/Medium/Low)
- [ ] Components JSON displays in formatted view

## Chrome Extension
- [ ] Extension loads in Chrome (Developer Mode → Load unpacked)
- [ ] Badge appears on YouTube video watch pages
- [ ] Badge shows score value (e.g., "Outlier 73.5")
- [ ] Background script calls API successfully

## Analytics Scheduler
- [ ] Scheduler runs (check logs)
- [ ] Latest `analytics_snapshots` rows have non-zero v2 fields:
  - `views_7d`, `views_28d`
  - `ctr_7d`, `ctr_28d`
  - `views_velocity_7d`, `views_velocity_28d`
  - `ctr_delta_7d`, `ctr_delta_28d`
  - `variance_7d`

## Performance
- [ ] API response time < 500ms
- [ ] Extension badge injection < 1s
- [ ] Scheduler completes within interval window

