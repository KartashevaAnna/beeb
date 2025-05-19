from app.utils.tools.auth_handler import AuthHandler


def test_decode_token():
    username = "Poblebonk"
    token = AuthHandler().encode_token(username=username)
    decoded_token = AuthHandler().decode_token(token)
    assert username in decoded_token["username"]
    assert "username" in decoded_token
    assert "exp" in decoded_token
