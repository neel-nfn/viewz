BEGIN;

CREATE TABLE IF NOT EXISTS ai_revisions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  job_id UUID NOT NULL REFERENCES ai_jobs(id) ON DELETE CASCADE,
  task_id UUID,
  revision_number INT NOT NULL,
  diff JSONB DEFAULT '{}'::jsonb,
  output_url TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_ai_revisions_task ON ai_revisions(task_id);

COMMIT;

