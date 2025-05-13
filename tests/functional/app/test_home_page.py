def test_home_page(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "платежи" in response.text
    assert "сводная таблица" in response.text
    assert "категории" in response.text
