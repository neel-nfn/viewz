import os
import psycopg
from psycopg.rows import dict_row


def _candidate_dsn_keys():
    # Prefer DATABASE_URL when present so local docker/dev can override a stale Supabase DSN.
    return ("DATABASE_URL", "SUPABASE_DB_URL")


def _is_valid_postgres_dsn(dsn: str) -> bool:
    return dsn.startswith("postgres://") or dsn.startswith("postgresql://")


def get_conn():
    for key in _candidate_dsn_keys():
        dsn = os.environ.get(key, "").strip()
        if not dsn:
            continue
        if not _is_valid_postgres_dsn(dsn):
            continue
        return psycopg.connect(dsn, row_factory=dict_row)

    present = {key: os.environ.get(key, "").strip() for key in _candidate_dsn_keys() if os.environ.get(key, "").strip()}
    if present:
        raise RuntimeError(
            "Invalid database DSN. Expected DATABASE_URL or SUPABASE_DB_URL to start with postgresql:// or postgres://, "
            f"got keys: {', '.join(f'{k}={v[:24]}...' for k, v in present.items())}"
        )
    raise RuntimeError("DATABASE_URL or SUPABASE_DB_URL missing")
