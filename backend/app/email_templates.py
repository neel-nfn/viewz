def invite_template(invite_link: str, org_name: str = "Viewz"):
    return f"""
    <div style="font-family:Inter,system-ui,Segoe UI,Arial,sans-serif;">
      <h2>You're invited to {org_name}</h2>
      <p>Click the button below to accept your invitation.</p>
      <p style="margin:24px 0;">
        <a href="{invite_link}" style="background:#4f46e5;color:#fff;padding:12px 18px;border-radius:8px;text-decoration:none;display:inline-block;">
          Accept Invite
        </a>
      </p>
      <p>If the button doesn't work, copy this link:</p>
      <p><a href="{invite_link}">{invite_link}</a></p>
    </div>
    """

