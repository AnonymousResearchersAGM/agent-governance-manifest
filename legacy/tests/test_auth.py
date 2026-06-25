from app.auth import can_access_resource, hash_password, verify_password


def test_password_round_trip():
    stored = hash_password("correct horse battery staple", salt="fixed-salt")
    assert verify_password("correct horse battery staple", stored)
    assert not verify_password("wrong password", stored)


def test_verify_password_rejects_malformed_hash():
    assert not verify_password("anything", "not-a-valid-stored-hash")


def test_can_access_resource_for_admin():
    assert can_access_resource("admin", resource_owner="alice", user_id="bob")


def test_can_access_resource_for_owner():
    assert can_access_resource("user", resource_owner="alice", user_id="alice")
    assert not can_access_resource("user", resource_owner="alice", user_id="bob")
