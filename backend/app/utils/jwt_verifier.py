import os, jwt, requests
from jwt.algorithms import RSAAlgorithm, ECAlgorithm
from typing import Optional

def verify_supabase_jwt(token: str, supabase_url: str, legacy_secret: Optional[bytes] = None):
    """
    Verify Supabase JWT token with support for ES256 (EC) and RS256 (RSA) from JWKS,
    with automatic fallback to HS256 when JWKS lookup fails (if legacy_secret is provided).
    
    Args:
        token: JWT token string
        supabase_url: Supabase project URL
        legacy_secret: Legacy HS256 secret (bytes) for fallback (optional)
    
    Returns:
        Decoded JWT payload
    
    Raises:
        Exception with clear error message if verification fails
    """
    # 1. Parse header
    header = jwt.get_unverified_header(token)
    alg = header.get("alg", "HS256")
    kid = header.get("kid")
    
    # 2. If header has kid, try JWKS first
    if kid:
        try:
            # Ensure no double slashes: supabase_url should already end without /
            supabase_url_clean = supabase_url.rstrip('/')
            JWKS_URL = f"{supabase_url_clean}/auth/v1/.well-known/jwks.json"
            jwks = requests.get(JWKS_URL, timeout=5).json()
            
            # Build keys dictionary supporting both RSA and EC keys
            keys = {}
            for k in jwks["keys"]:
                if k["kid"] == kid:
                    kty = k.get("kty")
                    if kty == "RSA":
                        keys[kid] = RSAAlgorithm.from_jwk(k)
                    elif kty == "EC" and k.get("crv") == "P-256":
                        keys[kid] = ECAlgorithm.from_jwk(k)
                        print("🧠 [JWT DEBUG] Using EC (P-256) key from JWKS")
                    else:
                        continue
            
            if kid in keys:
                key = keys[kid]
                return jwt.decode(token, key, algorithms=["ES256", "RS256"], audience="authenticated")
            else:
                # JWKS kid not found - fallback to HS256 if secret available
                print("⚠️ [JWT DEBUG] JWKS kid not found, falling back to HS256")
                if not legacy_secret:
                    print("🧠 [JWT DEBUG] No SUPABASE_JWT_SECRET, skipping HS256 fallback")
                    raise Exception("JWKS kid not found and no legacy secret provided")
                # Fallback to HS256
                return jwt.decode(token, legacy_secret, algorithms=["HS256"], audience="authenticated")
        except requests.RequestException as e:
            # Network error fetching JWKS - fallback to HS256 if secret available
            print(f"⚠️ [JWT DEBUG] JWKS fetch failed ({e}), falling back to HS256")
            if not legacy_secret:
                print("🧠 [JWT DEBUG] No SUPABASE_JWT_SECRET, skipping HS256 fallback")
                raise Exception(f"JWKS fetch failed and no legacy secret provided: {e}")
            return jwt.decode(token, legacy_secret, algorithms=["HS256"], audience="authenticated")
        except Exception as e:
            # Other JWKS errors - fallback to HS256 if secret available
            if "kid" in str(e).lower() or "unknown" in str(e).lower():
                print("⚠️ [JWT DEBUG] JWKS kid not found, falling back to HS256")
            else:
                print(f"⚠️ [JWT DEBUG] JWKS error ({e}), falling back to HS256")
            if not legacy_secret:
                print("🧠 [JWT DEBUG] No SUPABASE_JWT_SECRET, skipping HS256 fallback")
                raise Exception(f"JWKS verification failed and no legacy secret provided: {e}")
            try:
                return jwt.decode(token, legacy_secret, algorithms=["HS256"], audience="authenticated")
            except Exception as hs256_error:
                raise Exception(f"Invalid token signature (HS256 fallback failed: {hs256_error})")
    
    # 3. No kid - go straight to HS256 if secret available
    if not legacy_secret:
        print("🧠 [JWT DEBUG] No SUPABASE_JWT_SECRET, skipping HS256 fallback")
        raise Exception("No kid in token and no legacy secret provided")
    try:
        return jwt.decode(token, legacy_secret, algorithms=["HS256"], audience="authenticated")
    except jwt.InvalidSignatureError:
        raise Exception("Invalid token signature")
    except Exception as e:
        raise Exception(f"Token verification failed: {e}")

