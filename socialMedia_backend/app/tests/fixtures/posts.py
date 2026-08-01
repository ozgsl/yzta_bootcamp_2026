import uuid

import pytest

from app.models.social import Like, Post
from app.tests.fixtures.users import USER_A_ID, USER_B_ID, USER_C_ID


@pytest.fixture(scope="function")
def test_posts(db, test_users):
    """
    Creates mock posts in the database and returns their IDs and properties.
    """
    p1_id = uuid.uuid4()
    p2_id = uuid.uuid4()
    p3_id = uuid.uuid4()
    p4_id = uuid.uuid4()
    p5_id = uuid.uuid4()
    p6_id = uuid.uuid4()
    
    posts = [
        Post(id=p1_id, user_id=USER_A_ID, content="Public + consent", visibility="public", ai_training_consent=True, likes_count=2),
        Post(id=p2_id, user_id=USER_A_ID, content="Followers + consent", visibility="followers", ai_training_consent=True, likes_count=1),
        Post(id=p3_id, user_id=USER_A_ID, content="Private + no consent", visibility="private", ai_training_consent=False, likes_count=0),
        Post(id=p4_id, user_id=USER_A_ID, content="Public + no consent", visibility="public", ai_training_consent=False, likes_count=3),
        Post(id=p5_id, user_id=USER_B_ID, content="B public + consent", visibility="public", ai_training_consent=True, likes_count=1),
        Post(id=p6_id, user_id=USER_A_ID, content="Followers + no consent", visibility="followers", ai_training_consent=False, likes_count=0),
    ]
    
    db.add_all(posts)
    db.commit()
    
    # Likes
    likes = [
        Like(post_id=p1_id, user_id=USER_B_ID),
        Like(post_id=p1_id, user_id=USER_C_ID),
        Like(post_id=p2_id, user_id=USER_B_ID),
        Like(post_id=p4_id, user_id=USER_A_ID),
        Like(post_id=p4_id, user_id=USER_B_ID),
        Like(post_id=p4_id, user_id=USER_C_ID),
        Like(post_id=p5_id, user_id=USER_A_ID),
    ]
    
    db.add_all(likes)
    db.commit()
    
    return {
        "post-0001": {"id": str(p1_id), "visibility": "public",    "consent": 1, "owner": str(USER_A_ID)},
        "post-0002": {"id": str(p2_id), "visibility": "followers",  "consent": 1, "owner": str(USER_A_ID)},
        "post-0003": {"id": str(p3_id), "visibility": "private",    "consent": 0, "owner": str(USER_A_ID)},
        "post-0004": {"id": str(p4_id), "visibility": "public",     "consent": 0, "owner": str(USER_A_ID)},
        "post-0005": {"id": str(p5_id), "visibility": "public",     "consent": 1, "owner": str(USER_B_ID)},
        "post-0006": {"id": str(p6_id), "visibility": "followers",  "consent": 0, "owner": str(USER_A_ID)},
    }
