import os, psycopg
from psycopg.rows import dict_row
def get_conn():
    dsn = os.environ.get("SUPABASE_DB_URL")
    if not dsn:
        raise RuntimeError("SUPABASE_DB_URL missing")
    return psycopg.connect(dsn, row_factory=dict_row)
