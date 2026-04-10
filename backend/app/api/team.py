# backend/app/api/team.py
import os
from fastapi import APIRouter, Depends, HTTPException
from app.dependencies import require_session, get_supabase, require_org_context
from app.mailer import send_email
from app.email_templates import invite_template
from pydantic import BaseModel, EmailStr
from uuid import uuid4
from datetime import datetime, timezone

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

router = APIRouter(prefix="/api/v1/team", tags=["team"])

class InviteRequest(BaseModel):
    email: EmailStr
    role: str
    assigned_channel_ids: list[str] = []

@router.get("/list")
def list_team(user=Depends(require_session), org=Depends(require_org_context), sb=Depends(get_supabase)):
    # limited fields for non-admin/manager per Roles Matrix
    # admin/manager see full; writer/editor see limited (name+role if in same channels)
    # For v1 shell: return org roster with role/status
    q = sb.table("organization_users").select("user_id,role,status,users(email)").eq("org_id", org.id)
    data = q.execute().data
    
    # Mock data for development since we don't have real Supabase yet
    if not data:
        data = [
            {"user_id": user.id, "role": user.role, "status": "active", "users": {"email": "dev@example.com"}},
        ]
    
    team = []
    for row in data:
        entry = {
            "user_id": row["user_id"],
            "role": row["role"],
            "status": row["status"],
        }
        if user.role in ("admin","manager"):
            entry["email"] = row.get("users", {}).get("email", "")
        team.append(entry)
    
    return {"team": team}

@router.post("/invite", status_code=201)
def invite_member(payload: InviteRequest, user=Depends(require_session), org=Depends(require_org_context), sb=Depends(get_supabase)):
    if user.role not in ("admin","manager"):
        raise HTTPException(status_code=403, detail="forbidden")
    
    token = str(uuid4())
    
    # create pending invitation
    ins = sb.table("invitations").insert({
        "org_id": org.id,
        "email": str(payload.email).lower(),
        "role": payload.role,
        "token": token,
        "invited_by": user.id,
        "status": "pending",
    }).execute()
    
    if ins is None or getattr(ins, 'data', None) is None:
        # In mock mode, allow proceeding
        pass
    
    # optional: create a lightweight placeholder membership record with status=invited
    sb.table("organization_users").upsert({
        "org_id": org.id,
        "user_id": str(uuid4()),  # placeholder until accept flow binds real user
        "role": payload.role,
        "status": "invited",
    }).execute()
    
    # Send invite email
    invite_link = f"{FRONTEND_URL}/invite/accept/{token}"
    try:
        send_email(str(payload.email), "You're invited to Viewz Studio OS", invite_template(invite_link, "Viewz"))
    except Exception as e:
        print("Invite email send failed:", e)
    
    return {"invited": True, "token": token}


class AcceptInviteRequest(BaseModel):
    token: str


@router.post("/invite/accept")
def accept_invite(payload: AcceptInviteRequest, user=Depends(require_session), sb=Depends(get_supabase)):
    inv_q = sb.table("invitations").select("*").eq("token", payload.token).limit(1).execute().data
    if not inv_q:
        raise HTTPException(status_code=404, detail="invalid_token")
    inv = inv_q[0]
    if inv.get("status") != "pending":
        raise HTTPException(status_code=409, detail="already_consumed")
    expires_at = inv.get("expires_at")
    if expires_at:
        try:
            exp = datetime.fromisoformat(expires_at.replace("Z","+00:00"))
            if datetime.now(timezone.utc) > exp:
                raise HTTPException(status_code=410, detail="expired_token")
        except Exception:
            pass

    u_email = (getattr(user, "email", "") or "").lower()
    if u_email != (inv.get("email") or "").lower():
        raise HTTPException(status_code=403, detail="email_mismatch")

    org_id = inv.get("org_id")
    role = inv.get("role")

    sb.table("organization_users").upsert({
        "org_id": org_id,
        "user_id": user.id,
        "role": role,
        "status": "active",
    }, on_conflict="org_id,user_id").execute()

    now_iso = datetime.now(timezone.utc).isoformat()
    sb.table("invitations").update({
        "status": "accepted",
        "accepted_at": now_iso,
        "consumed_at": now_iso,
        "consumed_by": user.id,
    }).eq("id", inv.get("id")).execute()

    return {"accepted": True, "org_id": org_id, "role": role}

