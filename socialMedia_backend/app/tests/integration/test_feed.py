from sqlalchemy import select

from app.models.social import Follow, Post
from app.tests.fixtures.users import USER_A_ID, USER_B_ID, USER_C_ID


def _get_feed_post_ids(db, viewer_id):
    """Belirli bir viewer için feed'deki post_id'leri döndürür. (ORM üzerinden)"""
    following_ids = select(Follow.following_id).where(Follow.follower_id == viewer_id)
    query = select(Post.id).where(
        Post.user_id.in_(following_ids),
        (Post.visibility == 'public') | 
        ((Post.visibility == 'followers') & (Post.user_id.in_(following_ids)))
    ).order_by(Post.created_at.desc())
    
    return {str(post_id) for post_id in db.scalars(query).all()}

class TestBFeed:
    def test_b_sees_a_public_posts(self, db, test_users, test_posts):
        feed = _get_feed_post_ids(db, USER_B_ID)
        assert test_posts["post-0001"]["id"] in feed
        assert test_posts["post-0004"]["id"] in feed

    def test_b_sees_a_followers_posts(self, db, test_users, test_posts):
        feed = _get_feed_post_ids(db, USER_B_ID)
        assert test_posts["post-0002"]["id"] in feed
        assert test_posts["post-0006"]["id"] in feed

    def test_b_does_not_see_a_private_posts(self, db, test_users, test_posts):
        feed = _get_feed_post_ids(db, USER_B_ID)
        assert test_posts["post-0003"]["id"] not in feed

class TestCFeed:
    def test_c_sees_a_public_posts(self, db, test_users, test_posts):
        feed = _get_feed_post_ids(db, USER_C_ID)
        assert test_posts["post-0001"]["id"] not in feed
        assert test_posts["post-0004"]["id"] not in feed

    def test_c_does_not_see_a_followers_posts(self, db, test_users, test_posts):
        feed = _get_feed_post_ids(db, USER_C_ID)
        assert test_posts["post-0002"]["id"] not in feed
        assert test_posts["post-0006"]["id"] not in feed

    def test_c_does_not_see_a_private_posts(self, db, test_users, test_posts):
        feed = _get_feed_post_ids(db, USER_C_ID)
        assert test_posts["post-0003"]["id"] not in feed

class TestSelfFeed:
    def test_a_does_not_see_own_posts_in_feed(self, db, test_users, test_posts):
        feed = _get_feed_post_ids(db, USER_A_ID)
        a_posts = {
            test_posts["post-0001"]["id"], 
            test_posts["post-0002"]["id"], 
            test_posts["post-0003"]["id"], 
            test_posts["post-0004"]["id"], 
            test_posts["post-0006"]["id"]
        }
        assert feed.isdisjoint(a_posts)
