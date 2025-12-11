from fastapi import Depends, HTTPException
from app.core.security import get_current_user
from app.models.user import User


def require_role(*allowed_roles: str):
    """
    Dependency to ensure the logged-in user has the required role.
    Example:
        Depends(require_role("candidate"))
        Depends(require_role("recruiter", "hiring_manager"))
    """

    def role_checker(current_user: User = Depends(get_current_user)) -> User:

        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=403,
                detail=f"Access denied. Required roles: {allowed_roles}"
            )

        return current_user

    return role_checker
