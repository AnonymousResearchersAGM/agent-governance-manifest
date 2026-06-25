from demo_app.auth import authenticate_token, require_role


def test_authenticate_known_token():
    user = authenticate_token("alice-token")
    assert user is not None
    assert user.user_id == "alice"
    assert user.role == "contributor"


def test_authenticate_trims_accidental_whitespace():
    user = authenticate_token(" alice-token\n")
    assert user is not None
    assert user.user_id == "alice"


def test_authenticate_rejects_unknown_token():
    assert authenticate_token("wrong-token") is None
    assert authenticate_token("") is None


def test_require_role():
    maintainer = authenticate_token("maintainer-token")
    contributor = authenticate_token("alice-token")
    assert require_role(maintainer, {"maintainer"})
    assert not require_role(contributor, {"maintainer"})
