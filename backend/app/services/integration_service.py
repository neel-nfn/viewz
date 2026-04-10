from typing import Optional, Dict
from uuid import UUID
import os
import psycopg
from psycopg.rows import dict_row
from app.db.pg import get_conn
from app.utils.org import resolve_org_id
from app.utils.crypto_keys import encrypt_api_key, decrypt_api_key

def check_youtube_connected(org_id: UUID) -> bool:
    """Check if YouTube channel is connected for org."""
    org_id = resolve_org_id(org_id)
    try:
        with get_conn() as conn, conn.cursor() as cur:
            cur.execute("""
                select count(*) as cnt
                from youtube_channels
                where org_id = %s
            """, (org_id,))
            row = cur.fetchone()
            return (row.get("cnt", 0) or 0) > 0
    except Exception:
        return False

def get_ai_key_status(org_id: UUID, provider: str = "gemini") -> Dict:
    """Get AI key status for org."""
    org_id = resolve_org_id(org_id)
    try:
        with get_conn() as conn, conn.cursor() as cur:
            cur.execute("""
                select key_hint, enc_key_base64, iv_base64, tag_base64
                from ai_provider_keys
                where org_id = %s and provider = %s
                order by updated_at desc limit 1
            """, (org_id, provider))
            row = cur.fetchone()
            
            configured = bool(row and row.get("enc_key_base64") and row.get("iv_base64") and row.get("tag_base64"))
            hint = row.get("key_hint") if row else None
            
            return {
                "provider": provider,
                "configured": configured,
                "hint": hint
            }
    except Exception:
        return {"provider": provider, "configured": False, "hint": None}

def save_ai_key(org_id: UUID, provider: str, api_key: str) -> Dict:
    """Save encrypted AI key for org using AES-GCM."""
    org_id = resolve_org_id(org_id)
    enc_b64, iv_b64, tag_b64, hint = encrypt_api_key(api_key)
    
    try:
        with get_conn() as conn, conn.cursor() as cur:
            # Insert or update encrypted key (using unique constraint on org_id, provider)
            cur.execute("""
                insert into ai_provider_keys (org_id, provider, enc_key_base64, iv_base64, tag_base64, key_hint, updated_at)
                values (%s, %s, %s, %s, %s, %s, now())
                on conflict (org_id, provider)
                do update set 
                    enc_key_base64 = excluded.enc_key_base64,
                    iv_base64 = excluded.iv_base64,
                    tag_base64 = excluded.tag_base64,
                    key_hint = excluded.key_hint,
                    updated_at = now()
                returning id
            """, (org_id, provider, enc_b64, iv_b64, tag_b64, hint))
            row = cur.fetchone()
            conn.commit()
            
            return {"saved": True, "provider": provider, "hint": hint}
    except Exception as e:
        raise RuntimeError(f"save_ai_key_failed: {str(e)}")

def delete_ai_key(org_id: UUID, provider: str = "gemini") -> Dict:
    """Delete AI key for org."""
    org_id = resolve_org_id(org_id)
    try:
        with get_conn() as conn, conn.cursor() as cur:
            cur.execute("""
                delete from ai_provider_keys
                where org_id = %s and provider = %s
            """, (org_id, provider))
            conn.commit()
            return {"deleted": True}
    except Exception as e:
        raise RuntimeError(f"delete_ai_key_failed: {str(e)}")

def load_ai_key_for_org(org_id: UUID, provider: str = "gemini") -> Optional[str]:
    """Load and decrypt AI key for org (runtime use)."""
    org_id = resolve_org_id(org_id)
    try:
        with get_conn() as conn, conn.cursor() as cur:
            cur.execute("""
                select enc_key_base64, iv_base64, tag_base64
                from ai_provider_keys
                where org_id = %s and provider = %s
                order by updated_at desc limit 1
            """, (org_id, provider))
            row = cur.fetchone()
            
        if not row or not row.get("enc_key_base64"):
            return None
        
        return decrypt_api_key(row["enc_key_base64"], row["iv_base64"], row["tag_base64"])
    except Exception as e:
        # Log error but don't expose decryption failures to caller
        print(f"[ERROR] Failed to load AI key for org {org_id}: {e}")
        return None
