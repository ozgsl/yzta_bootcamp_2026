import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.models.base import get_db


@pytest.fixture()
def client(db):
    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

def test_like_unlike_post(client, test_users, test_posts):
    user_id = test_users["B"]
    post_id = test_posts["post-0003"]["id"] # Has 0 likes initially

    # Like
    like = client.post("/likes/", json={"user_id": user_id, "post_id": post_id})
    assert like.status_code == 200

    # Unlike
    unlike = client.request("DELETE", "/likes/", json={"user_id": user_id, "post_id": post_id})
    assert unlike.status_code == 200

def test_save_unsave_post(client, test_users, test_posts):
    user_id = test_users["B"]
    post_id = test_posts["post-0001"]["id"]

    # Save
    save = client.post(f"/posts/{post_id}/save?user_id={user_id}")
    assert save.status_code == 200

    # Get saved posts
    saved = client.get(f"/posts/users/{user_id}/saved_posts")
    assert saved.status_code == 200
    assert len(saved.json()) == 1

    # Unsave
    unsave = client.delete(f"/posts/{post_id}/save?user_id={user_id}")
    assert unsave.status_code == 200

def test_add_and_list_comments(client, test_users, test_posts):
    user_id = test_users["A"]
    post_id = test_posts["post-0001"]["id"]

    # Add Comment
    created = client.post(
        "/likes/comments",
        json={"user_id": user_id, "post_id": post_id, "content": "Harika kombin!"},
    )
    assert created.status_code == 200
    assert created.json()["id"]

    # List Comments
    comments = client.get(f"/likes/comments/{post_id}")
    assert comments.status_code == 200
    assert len(comments.json()) >= 1
    
    # One of them should be "Harika kombin!"
    contents = [c["content"] for c in comments.json()]
    assert "Harika kombin!" in contents
