from fastapi.testclient import TestClient
from crud_operations import app  

client = TestClient(app)

def test_create_user():
    response = client.post("/users/", json={"username": "test_user"})
    assert response.status_code == 200
    assert response.json()["username"] == "test_user"

def test_read_user():
    response = client.post("/users/", json={"username": "read_test_user"})
    user_id = response.json()["id"]

    response = client.get(f"/users/{user_id}")
    assert response.status_code == 200
    assert response.json()["username"] == "read_test_user"

def test_update_user():
    response = client.post("/users/", json={"username": "update_test_user"})
    user_id = response.json()["id"]

    response = client.put(f"/users/{user_id}", json={"username": "updated_username"})
    assert response.status_code == 200
    assert response.json()["username"] == "updated_username"

def test_delete_user():
    response = client.post("/users/", json={"username": "delete_test_user"})
    user_id = response.json()["id"]

    response = client.delete(f"/users/{user_id}")
    assert response.status_code == 200
    assert response.json()["message"] == "User deleted successfully"


def test_create_photo():
    response = client.post("/photos/", json={"title": "test_photo", "url": "http://example.com/test.jpg"})
    assert response.status_code == 200
    assert response.json()["title"] == "test_photo"

def test_read_photo():
    create_response = client.post("/photos/", json={"title": "test_photo", "url": "http://example.com/test.jpg"})
    photo_id = create_response.json()["id"]

    read_response = client.get(f"/photos/{photo_id}")
    assert read_response.status_code == 200
    assert read_response.json()["title"] == "test_photo"

def test_update_photo():
    create_response = client.post("/photos/", json={"title": "test_photo", "url": "http://example.com/test.jpg"})
    photo_id = create_response.json()["id"]

    update_response = client.put(f"/photos/{photo_id}", json={"title": "updated_photo", "url": "http://example.com/updated.jpg"})
    assert update_response.status_code == 200
    assert update_response.json()["title"] == "updated_photo"

def test_delete_photo():
    create_response = client.post("/photos/", json={"title": "test_photo", "url": "http://example.com/test.jpg"})
    photo_id = create_response.json()["id"]

    delete_response = client.delete(f"/photos/{photo_id}")
    assert delete_response.status_code == 200
    assert delete_response.json()["message"] == "Photo deleted successfully"
