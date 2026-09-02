async def test_login_endpoint_success(client, persisted_user):
    user, plain_password = persisted_user

    response = await client.post(
        "/auth/token",
        data={"username": user.username, "password": plain_password},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert "access_token" in body


async def test_login_endpoint_invalid_credentials(client, persisted_user):
    user, _ = persisted_user

    response = await client.post(
        "/auth/token",
        data={"username": user.username, "password": "wrong-password"},
    )

    assert response.status_code == 401