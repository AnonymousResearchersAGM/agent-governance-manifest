"""Token authentication for the demo task tracker."""

from __future__ import annotations

import hashlib
import hmac
from dataclasses import dataclass


@dataclass(frozen=True)
class User:
    user_id: str
    role: str


def hash_token(token: str) -> str:
    if not token:
        raise ValueError("token is required")
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


TOKEN_TABLE = {
    hash_token("maintainer-token"): User(user_id="maintainer", role="maintainer"),
    hash_token("alice-token"): User(user_id="alice", role="contributor"),
}


def normalize_token(token: str) -> str:
    return token.strip()


def authenticate_token(token: str) -> User | None:
    normalized = normalize_token(token)
    if not normalized:
        return None
    candidate = hash_token(normalized)
    for stored_hash, user in TOKEN_TABLE.items():
        if hmac.compare_digest(candidate, stored_hash):
            return user
    return None


def require_role(user: User | None, allowed_roles: set[str]) -> bool:
    return user is not None and user.role in allowed_roles
