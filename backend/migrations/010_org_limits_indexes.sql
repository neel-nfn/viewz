BEGIN;

CREATE INDEX IF NOT EXISTS idx_ai_jobs_org_user_day ON ai_jobs(org_id, created_by, created_at);

CREATE INDEX IF NOT EXISTS idx_voice_jobs_org_user_day ON voice_jobs(org_id, created_by, created_at);

COMMIT;

