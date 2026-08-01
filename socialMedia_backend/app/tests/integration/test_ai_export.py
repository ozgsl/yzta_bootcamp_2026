import json

from sqlalchemy import select

from app.models.social import Post, TrainingDataExport
from app.services.ai_export import run_export
from app.tests.fixtures.users import USER_A_ID


class TestAIExportFiltering:
    def test_consent_false_not_exported(self, db, tmp_path, test_users, test_posts):
        records = run_export(db=db, exports_dir=tmp_path)
        exported_ids = {r["post_id"] for r in records}
        assert test_posts["post-0004"]["id"] not in exported_ids
        assert test_posts["post-0003"]["id"] not in exported_ids
        assert test_posts["post-0006"]["id"] not in exported_ids

    def test_private_visibility_not_exported(self, db, tmp_path, test_users, test_posts):
        new_post = Post(user_id=USER_A_ID, image_url="https://example.com/posts/priv.jpg", visibility="private", ai_training_consent=True)
        db.add(new_post)
        db.commit()

        records = run_export(db=db, exports_dir=tmp_path)
        exported_ids = {r["post_id"] for r in records}
        assert str(new_post.id) not in exported_ids

    def test_public_consent_true_exported(self, db, tmp_path, test_users, test_posts):
        records = run_export(db=db, exports_dir=tmp_path)
        exported_ids = {r["post_id"] for r in records}
        assert test_posts["post-0001"]["id"] in exported_ids

    def test_followers_consent_true_exported(self, db, tmp_path, test_users, test_posts):
        records = run_export(db=db, exports_dir=tmp_path)
        exported_ids = {r["post_id"] for r in records}
        assert test_posts["post-0002"]["id"] in exported_ids

class TestAIExportIdempotency:
    def test_double_export_no_duplicates(self, db, tmp_path, test_users, test_posts):
        first_run = run_export(db=db, exports_dir=tmp_path)
        assert len(first_run) > 0
        first_ids = {r["post_id"] for r in first_run}

        second_run = run_export(db=db, exports_dir=tmp_path)
        second_ids = {r["post_id"] for r in second_run}
        assert first_ids.isdisjoint(second_ids)

    def test_second_run_returns_empty(self, db, tmp_path, test_users, test_posts):
        run_export(db=db, exports_dir=tmp_path)
        second_run = run_export(db=db, exports_dir=tmp_path)
        assert len(second_run) == 0

class TestAIExportJSONContract:
    def test_json_structure(self, db, tmp_path, test_users, test_posts):
        records = run_export(db=db, exports_dir=tmp_path)
        assert len(records) > 0
        for rec in records:
            assert "post_id" in rec
            assert "image_url" in rec
            assert "outfit_items" in rec
            assert "created_at" in rec
            assert isinstance(rec["outfit_items"], list)
            for item in rec["outfit_items"]:
                assert "item_id" in item
                assert "category" in item
                assert "image_url" in item

    def test_export_file_written(self, db, tmp_path, test_users, test_posts):
        run_export(db=db, exports_dir=tmp_path)
        json_files = list(tmp_path.glob("training_export_*.json"))
        assert len(json_files) >= 1
        with open(json_files[0], "r", encoding="utf-8") as f:
            data = json.load(f)
        assert isinstance(data, list)
        assert len(data) > 0

    def test_training_data_export_table_populated(self, db, tmp_path, test_users, test_posts):
        records = run_export(db=db, exports_dir=tmp_path)
        rows = db.scalars(select(TrainingDataExport)).all()
        # Ensure that new records were added (comparing with what was run in this scope)
        assert len(rows) >= len(records) 
