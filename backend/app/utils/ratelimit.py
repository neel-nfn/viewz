import os
import datetime

# Mock DB for development (when DATABASE_URL not set)
def _db():
    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        # Return mock connection for dev
        class MockConn:
            def cursor(self):
                return MockCursor()
            def __enter__(self):
                return self
            def __exit__(self, *args):
                pass
        return MockConn()
    try:
        import psycopg
        return psycopg.connect(db_url, autocommit=True)
    except ImportError:
        # Fallback to mock if psycopg not installed
        class MockConn:
            def cursor(self):
                return MockCursor()
            def __enter__(self):
                return self
            def __exit__(self, *args):
                pass
        return MockConn()

class MockCursor:
    def execute(self, query, params):
        self.query = query
        self.params = params
    def fetchone(self):
        # In dev mode, always return 0 (no limit exceeded)
        return [0]
    def __enter__(self):
        return self
    def __exit__(self, *args):
        pass

def _window_start():
    now = datetime.datetime.utcnow()
    return now - datetime.timedelta(days=1)

def ai_limit_for_role(role: str) -> int:
    if role == "admin":
        return int(os.environ.get("AI_LIMITS_ADMIN_PER_DAY", "200"))
    if role == "manager":
        return int(os.environ.get("AI_LIMITS_MANAGER_PER_DAY", "60"))
    return int(os.environ.get("AI_LIMITS_WRITER_PER_DAY", "30"))

def voice_limit_for_role(role: str) -> int:
    if role == "admin":
        return int(os.environ.get("VOICE_LIMITS_ADMIN_PER_DAY", "200"))
    if role == "manager":
        return int(os.environ.get("VOICE_LIMITS_MANAGER_PER_DAY", "60"))
    return int(os.environ.get("VOICE_LIMITS_EDITOR_PER_DAY", "30"))

def ai_under_limit_org(org_id: str, user_id: str, role: str) -> bool:
    start = _window_start()
    with _db() as conn, conn.cursor() as cur:
        cur.execute("SELECT COUNT(1) FROM ai_jobs WHERE org_id=%s AND created_by=%s AND created_at>=%s", (org_id, user_id, start))
        used = cur.fetchone()[0]
    return used < ai_limit_for_role(role)

def voice_under_limit_org(org_id: str, user_id: str, role: str) -> bool:
    start = _window_start()
    with _db() as conn, conn.cursor() as cur:
        cur.execute("SELECT COUNT(1) FROM voice_jobs WHERE org_id=%s AND created_by=%s AND created_at>=%s", (org_id, user_id, start))
        used = cur.fetchone()[0]
    return used < voice_limit_for_role(role)

