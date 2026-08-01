from sqlalchemy import select

from app.models.social import Follow, Post, TrainingDataExport
from app.tests.fixtures.users import USER_A_ID, USER_B_ID, USER_C_ID


def _get_profile_post_ids(db, profile_owner_id, viewer_id):
    following_ids = select(Follow.following_id).where(Follow.follower_id == viewer_id)
    query = select(Post.id).where(
        Post.user_id == profile_owner_id,
        (Post.user_id == viewer_id) |
        (Post.visibility == 'public') |
        ((Post.visibility == 'followers') & (Post.user_id.in_(following_ids)))
    ).order_by(Post.created_at.desc())
    return {str(pid) for pid in db.scalars(query).all()}

def _get_ai_exportable_post_ids(db):
    exported_ids = select(TrainingDataExport.post_id)
    query = select(Post.id).where(
        Post.ai_training_consent == True,
        Post.visibility != 'private',
        Post.id.not_in(exported_ids)
    )
    return {str(pid) for pid in db.scalars(query).all()}

class TestScenario1PublicConsentTrue:
    def test_a_sees_on_profile(self, db, test_users, test_posts):
        assert test_posts["post-0001"]["id"] in _get_profile_post_ids(db, USER_A_ID, USER_A_ID)

    def test_b_sees_on_profile(self, db, test_users, test_posts):
        assert test_posts["post-0001"]["id"] in _get_profile_post_ids(db, USER_A_ID, USER_B_ID)

    def test_c_sees_on_profile(self, db, test_users, test_posts):
        assert test_posts["post-0001"]["id"] in _get_profile_post_ids(db, USER_A_ID, USER_C_ID)

    def test_ai_export_includes(self, db, test_users, test_posts):
        assert test_posts["post-0001"]["id"] in _get_ai_exportable_post_ids(db)

class TestScenario2PublicConsentFalse:
    def test_a_sees_on_profile(self, db, test_users, test_posts):
        assert test_posts["post-0004"]["id"] in _get_profile_post_ids(db, USER_A_ID, USER_A_ID)

    def test_b_sees_on_profile(self, db, test_users, test_posts):
        assert test_posts["post-0004"]["id"] in _get_profile_post_ids(db, USER_A_ID, USER_B_ID)

    def test_c_sees_on_profile(self, db, test_users, test_posts):
        assert test_posts["post-0004"]["id"] in _get_profile_post_ids(db, USER_A_ID, USER_C_ID)

    def test_ai_export_excludes(self, db, test_users, test_posts):
        assert test_posts["post-0004"]["id"] not in _get_ai_exportable_post_ids(db)

class TestScenario3FollowersConsentTrue:
    def test_a_sees_on_profile(self, db, test_users, test_posts):
        assert test_posts["post-0002"]["id"] in _get_profile_post_ids(db, USER_A_ID, USER_A_ID)

    def test_b_sees_on_profile(self, db, test_users, test_posts):
        assert test_posts["post-0002"]["id"] in _get_profile_post_ids(db, USER_A_ID, USER_B_ID)

    def test_c_does_not_see_on_profile(self, db, test_users, test_posts):
        assert test_posts["post-0002"]["id"] not in _get_profile_post_ids(db, USER_A_ID, USER_C_ID)

    def test_ai_export_includes(self, db, test_users, test_posts):
        assert test_posts["post-0002"]["id"] in _get_ai_exportable_post_ids(db)

class TestScenario4FollowersConsentFalse:
    def test_a_sees_on_profile(self, db, test_users, test_posts):
        assert test_posts["post-0006"]["id"] in _get_profile_post_ids(db, USER_A_ID, USER_A_ID)

    def test_b_sees_on_profile(self, db, test_users, test_posts):
        assert test_posts["post-0006"]["id"] in _get_profile_post_ids(db, USER_A_ID, USER_B_ID)

    def test_c_does_not_see_on_profile(self, db, test_users, test_posts):
        assert test_posts["post-0006"]["id"] not in _get_profile_post_ids(db, USER_A_ID, USER_C_ID)

    def test_ai_export_excludes(self, db, test_users, test_posts):
        assert test_posts["post-0006"]["id"] not in _get_ai_exportable_post_ids(db)

class TestScenario5PrivateConsentTrue:
    def _insert_private_consent_post(self, db) -> str:
        new_post = Post(user_id=USER_A_ID, image_url="https://example.com/p", visibility="private", ai_training_consent=True)
        db.add(new_post)
        db.commit()
        return str(new_post.id)

    def test_a_sees_on_profile(self, db, test_users, test_posts):
        pid = self._insert_private_consent_post(db)
        assert pid in _get_profile_post_ids(db, USER_A_ID, USER_A_ID)

    def test_b_does_not_see_on_profile(self, db, test_users, test_posts):
        pid = self._insert_private_consent_post(db)
        assert pid not in _get_profile_post_ids(db, USER_A_ID, USER_B_ID)

    def test_c_does_not_see_on_profile(self, db, test_users, test_posts):
        pid = self._insert_private_consent_post(db)
        assert pid not in _get_profile_post_ids(db, USER_A_ID, USER_C_ID)

    def test_ai_export_excludes(self, db, test_users, test_posts):
        pid = self._insert_private_consent_post(db)
        assert pid not in _get_ai_exportable_post_ids(db)

class TestScenario6PrivateConsentFalse:
    def test_a_sees_on_profile(self, db, test_users, test_posts):
        assert test_posts["post-0003"]["id"] in _get_profile_post_ids(db, USER_A_ID, USER_A_ID)

    def test_b_does_not_see_on_profile(self, db, test_users, test_posts):
        assert test_posts["post-0003"]["id"] not in _get_profile_post_ids(db, USER_A_ID, USER_B_ID)

    def test_c_does_not_see_on_profile(self, db, test_users, test_posts):
        assert test_posts["post-0003"]["id"] not in _get_profile_post_ids(db, USER_A_ID, USER_C_ID)

    def test_ai_export_excludes(self, db, test_users, test_posts):
        assert test_posts["post-0003"]["id"] not in _get_ai_exportable_post_ids(db)
