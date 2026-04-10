from fastapi import Depends, HTTPException, Request
from functools import lru_cache
from datetime import datetime, timezone
import os

# Placeholder user session model
class SessionUser:
    def __init__(self, id: str, role: str, email: str | None = None):
        self.id = id
        self.role = role
        self.email = email

# Placeholder org context model
class OrgContext:
    def __init__(self, id: str):
        self.id = id

# Mock session dependency - will be replaced with real auth in production
def require_session(request: Request) -> SessionUser:
    token = request.cookies.get("viewz_session")
    if not token:
        raise HTTPException(status_code=401, detail="unauthorized")
    # Check if there's a user_email cookie to support testing different users
    user_email = request.cookies.get("user_email", "dev@example.com")
    # For now, return a mock admin user (or use email from cookie for testing)
    # In production, validate token and return actual user
    user_id = "dev_user_1" if user_email == "dev@example.com" else f"user_{user_email.replace('@', '_').replace('+', '_')}"
    user_role = "admin" if user_email == "dev@example.com" else "writer"
    return SessionUser(id=user_id, role=user_role, email=user_email)

# Mock org context - will be replaced with real org resolution
def require_org_context(user: SessionUser = Depends(require_session)) -> OrgContext:
    # For now, return a mock org
    # In production, resolve from user's primary org or request header
    return OrgContext(id=str("00000000-0000-0000-0000-000000000001"))

# In-memory stores for mock Supabase (module-level for persistence)
_invitations_store: dict = {}
_organization_users_store: list = []

# Mock Supabase client - will be replaced with real client in production
def get_supabase():
    # Placeholder - in production, initialize real Supabase client
    class MockSupabase:
        class Table:
            def __init__(self, name):
                self.name = name
            
            def select(self, fields):
                self.fields = fields
                return self
            
            def eq(self, field, value):
                self.filters = getattr(self, 'filters', {})
                self.filters[field] = value
                return self
            
            def limit(self, n: int):
                self._limit = n
                return self
            
            def insert(self, data):
                self.insert_data = data
                return self
            
            def upsert(self, data, on_conflict: str | None = None):
                self.upsert_data = data
                self.on_conflict = on_conflict
                return self
            
            def update(self, data):
                self.update_data = data
                return self
            
            def execute(self):
                # Mock response
                class Response:
                    def __init__(self, data):
                        self.data = data
                
                # Handle invitations table
                if self.name == 'invitations':
                    if hasattr(self, 'insert_data'):
                        # Store invitation by token
                        inv_data = self.insert_data.copy()
                        inv_data.setdefault('id', f"inv_{len(_invitations_store)}")
                        inv_data.setdefault('expires_at', None)
                        inv_data.setdefault('created_at', datetime.now(timezone.utc).isoformat())
                        _invitations_store[inv_data['token']] = inv_data
                        return Response([inv_data])
                    
                    if hasattr(self, 'update_data') and hasattr(self, 'filters') and self.filters.get('id'):
                        # Update invitation
                        inv_id = self.filters['id']
                        for token, inv in _invitations_store.items():
                            if inv.get('id') == inv_id:
                                inv.update(self.update_data)
                                return Response([inv])
                        return Response([])
                    
                    if hasattr(self, 'filters') and self.filters.get('token'):
                        # Look up invitation by token
                        token = self.filters['token']
                        if token in _invitations_store:
                            return Response([_invitations_store[token]])
                        return Response([])
                    
                    return Response([])
                
                # Handle organization_users table
                if self.name == 'organization_users':
                    if hasattr(self, 'upsert_data'):
                        # Find existing or add new
                        upsert_data = self.upsert_data.copy()
                        if self.on_conflict == "org_id,user_id":
                            # Remove existing with same org_id and user_id
                            _organization_users_store[:] = [
                                u for u in _organization_users_store
                                if not (u.get('org_id') == upsert_data.get('org_id') and u.get('user_id') == upsert_data.get('user_id'))
                            ]
                        _organization_users_store.append(upsert_data)
                        return Response([upsert_data])
                    
                    if hasattr(self, 'filters'):
                        # Filter organization_users
                        filtered = []
                        for user in _organization_users_store:
                            match = True
                            for key, value in self.filters.items():
                                if user.get(key) != value:
                                    match = False
                                    break
                            if match:
                                # Add email if available from user lookup
                                user_copy = user.copy()
                                # Try to get email from user_id pattern or from a separate lookup
                                user_email = user_copy.get('email')
                                if not user_email:
                                    if user_copy.get('user_id') == 'dev_user_1':
                                        user_email = 'dev@example.com'
                                    elif user_copy.get('user_id', '').startswith('user_'):
                                        # Extract email from user_id pattern: user_idhossain111_dev_gmail.com
                                        user_id = user_copy.get('user_id', '')
                                        if '_gmail.com' in user_id:
                                            user_email = user_id.replace('user_', '').replace('_', '@').replace('_gmail.com', '@gmail.com')
                                        elif '_dev' in user_id:
                                            user_email = user_id.replace('user_', '').replace('_', '+').replace('_gmail.com', '@gmail.com')
                                user_copy['users'] = {'email': user_email or ''}
                                filtered.append(user_copy)
                        if not filtered and self.filters.get('org_id'):
                            # Return default admin user if empty
                            return Response([
                                {'user_id': 'dev_user_1', 'role': 'admin', 'status': 'active', 'users': {'email': 'dev@example.com'}}
                            ])
                        return Response(filtered)
                    
                    return Response(_organization_users_store)
                
                return Response([])
        
        def table(self, name):
            return self.Table(name)
    
    return MockSupabase()

