from fastapi import status


def test_home_page(client):
    response = client.get("/")
    assert response.status_code == status.HTTP_200_OK
    assert response.template.name == "pages/home_page.html"
