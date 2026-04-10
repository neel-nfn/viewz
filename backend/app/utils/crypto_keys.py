import base64
import os
from typing import Tuple
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

def _get_kek() -> bytes:
    """Get Key Encryption Key from environment."""
    b64 = os.getenv("AI_KEY_KEK_B64", "")
    if not b64:
        raise RuntimeError("AI_KEY_KEK_B64 missing")
    try:
        raw = base64.b64decode(b64)
    except Exception as e:
        raise RuntimeError("AI_KEY_KEK_B64 invalid base64") from e
    if len(raw) not in (16, 24, 32):
        raise RuntimeError("AI_KEY_KEK_B64 must decode to 16/24/32 bytes for AES")
    return raw

def encrypt_api_key(plain_key: str) -> Tuple[str, str, str, str]:
    """
    Encrypt API key using AES-GCM.
    Returns (enc_b64, iv_b64, tag_b64, hint)
    """
    kek = _get_kek()
    aes = AESGCM(kek)
    iv = os.urandom(12)  # 96-bit nonce for AES-GCM
    pt = plain_key.encode("utf-8")
    ct = aes.encrypt(iv, pt, None)  # ciphertext||tag
    
    # Split tag from tail (16 bytes)
    ciphertext, tag = ct[:-16], ct[-16:]
    
    enc_b64 = base64.b64encode(ciphertext).decode()
    iv_b64 = base64.b64encode(iv).decode()
    tag_b64 = base64.b64encode(tag).decode()
    
    # hint: provider prefix or last 4 chars for UX
    hint = _key_hint(plain_key)
    
    return enc_b64, iv_b64, tag_b64, hint

def decrypt_api_key(enc_b64: str, iv_b64: str, tag_b64: str) -> str:
    """Decrypt API key using AES-GCM."""
    kek = _get_kek()
    aes = AESGCM(kek)
    ct = base64.b64decode(enc_b64)
    iv = base64.b64decode(iv_b64)
    tag = base64.b64decode(tag_b64)
    combined = ct + tag
    pt = aes.decrypt(iv, combined, None)
    return pt.decode("utf-8")

def _key_hint(key: str) -> str:
    """Generate a basic, non-sensitive hint for UI."""
    prefix = "Gemini"
    tail = key[-4:] if len(key) >= 4 else "****"
    return f"{prefix} · …{tail}"

