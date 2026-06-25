"""Authentication logic used to exercise critical-risk changes."""

import hashlib
import hmac
import secrets


def hash_password(password: str, salt: str | None = None) -> str:
    """Create a salted password hash for the prototype."""
    if not password:
        raise ValueError("password is required")
    chosen_salt = salt or secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        chosen_salt.encode("utf-8"),
        100_000,
    ).hex()
    return f"{chosen_salt}${digest}"


def verify_password(password: str, stored_hash: str) -> bool:
    """Verify a password against a salt$hash string."""
    if "$" not in stored_hash:
        return False
    salt, expected_digest = stored_hash.split("$", 1)
    actual = hash_password(password, salt).split("$", 1)[1]
    return hmac.compare_digest(actual, expected_digest)


def can_access_resource(user_role: str, resource_owner: str, user_id: str) -> bool:
    """Simple authorization rule for the prototype."""
    if user_role == "admin":
        return True
    return resource_owner == user_id

