import uuid

import pytest

from app.models.social import Follow, Profile

# Fixed UUIDs for testing consistency if needed, though dynamic is better for clean tests
USER_A_ID = uuid.uuid4()
USER_B_ID = uuid.uuid4()
USER_C_ID = uuid.uuid4()

@pytest.fixture(scope="function")
def test_users(db):
    """
    Creates basic users in the database and returns their IDs.
    User A: Post owner (elif_style)
    User B: Follows A (ahmet_trendy)
    User C: Does not follow A (zeynep_chic)
    """
    user_a = Profile(id=USER_A_ID, email="elif@example.com", username="elif_style", display_name="Elif Yılmaz")
    user_b = Profile(id=USER_B_ID, email="ahmet@example.com", username="ahmet_trendy", display_name="Ahmet Demir")
    user_c = Profile(id=USER_C_ID, email="zeynep@example.com", username="zeynep_chic", display_name="Zeynep Kaya")
    
    db.add_all([user_a, user_b, user_c])
    db.commit()
    
    # B follows A
    follow = Follow(follower_id=USER_B_ID, following_id=USER_A_ID)
    db.add(follow)
    db.commit()
    
    return {
        "A": str(USER_A_ID),
        "B": str(USER_B_ID),
        "C": str(USER_C_ID),
    }
