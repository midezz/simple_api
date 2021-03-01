from starlette.testclient import TestClient
from example import app


def test_homepage():
    client = TestClient(app)
    response = client.get('/')
    assert response.status_code == 200
    assert 'Test starlette' in response.content
