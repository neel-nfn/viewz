from typing import List, Optional
from uuid import UUID
import os
import psycopg
from psycopg.rows import dict_row
from app.schemas.feedback_schemas import FeedbackCreate, FeedbackUpdate, FeedbackPublic

def get_conn():
    dsn = os.getenv("SUPABASE_DB_URL")
    if not dsn:
        raise RuntimeError("SUPABASE_DB_URL missing")
    return psycopg.connect(dsn, row_factory=dict_row)

def create_feedback(payload: FeedbackCreate) -> FeedbackPublic:
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("""
          insert into feedback_reports
          (org_id,user_id,channel_id,url,category,severity,title,description,metadata)
          values (%s,%s,%s,%s,%s,%s,%s,%s,coalesce(%s,'{}'::jsonb))
          returning id,org_id,user_id,channel_id,url,category,severity,title,description,metadata,status,created_at,updated_at
        """, (
            str(payload.org_id),
            str(payload.user_id) if payload.user_id else None,
            str(payload.channel_id) if payload.channel_id else None,
            payload.url,
            payload.category,
            payload.severity,
            payload.title,
            payload.description,
            payload.metadata or {}
        ))
        row = cur.fetchone()
        conn.commit()
    return FeedbackPublic(**row)

def list_feedback(org_id: UUID, status: Optional[str]=None, limit:int=100, offset:int=0) -> List[FeedbackPublic]:
    with get_conn() as conn, conn.cursor() as cur:
        if status:
            cur.execute("""
              select * from feedback_reports
              where org_id=%s and status=%s
              order by created_at desc limit %s offset %s
            """,(str(org_id), status, limit, offset))
        else:
            cur.execute("""
              select * from feedback_reports
              where org_id=%s
              order by created_at desc limit %s offset %s
            """,(str(org_id), limit, offset))
        rows = cur.fetchall()
    return [FeedbackPublic(**r) for r in rows]

def update_feedback_status(org_id: UUID, feedback_id: UUID, update: FeedbackUpdate) -> FeedbackPublic:
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("""
          update feedback_reports
          set status=%s, updated_at=now()
          where id=%s and org_id=%s
          returning *
        """,(update.status, str(feedback_id), str(org_id)))
        row = cur.fetchone()
        conn.commit()
    if not row:
        raise ValueError("not_found")
    return FeedbackPublic(**row)

