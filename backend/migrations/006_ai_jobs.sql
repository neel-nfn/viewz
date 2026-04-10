BEGIN;

CREATE TABLE IF NOT EXISTS ai_jobs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  org_id UUID NOT NULL,
  channel_id UUID NOT NULL,
  task_id UUID,
  persona TEXT NOT NULL,
  mode TEXT NOT NULL,
  model_used TEXT,
  prompt_text TEXT NOT NULL,
  output_url TEXT,
  status TEXT NOT NULL DEFAULT 'succeeded',
  created_by UUID NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_ai_jobs_task ON ai_jobs(task_id);
CREATE INDEX IF NOT EXISTS idx_ai_jobs_org ON ai_jobs(org_id, channel_id, created_at);

COMMIT;

