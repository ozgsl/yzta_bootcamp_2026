import sqlite3
import uuid
from passlib.context import CryptContext
from datetime import datetime

db = sqlite3.connect('database.db')
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

user_id = str(uuid.uuid4())
username = "yeni_test_user"
email = "yeni_test_user@gmail.com"
password = "testuser123"
hashed_pw = pwd_context.hash(password)
display_name = "Yeni Test"
bio = "Test hesabi"

db.execute("DELETE FROM users WHERE email=?", (email,))

db.execute(
    'INSERT INTO users (user_id, username, email, password_hash, display_name, bio) VALUES (?, ?, ?, ?, ?, ?)',
    (user_id, username, email, hashed_pw, display_name, bio)
)

images = [
    "https://images.unsplash.com/photo-1434389678232-04ce6c40e536?auto=format&fit=crop&w=800",
    "https://images.unsplash.com/photo-1550614000-4b95d4ed16bd?auto=format&fit=crop&w=800"
]
for i, img in enumerate(images):
    post_id = str(uuid.uuid4())
    db.execute(
        'INSERT INTO posts (post_id, user_id, image_url, caption, visibility) VALUES (?, ?, ?, ?, ?)',
        (post_id, user_id, img, f"Post {i+1}", 'public')
    )

other_posts = db.execute("SELECT post_id FROM posts WHERE user_id != ? LIMIT 3", (user_id,)).fetchall()
for p in other_posts:
    db.execute(
        "INSERT OR IGNORE INTO saved_posts (user_id, post_id, saved_at) VALUES (?,?,?)",
        (user_id, p[0], datetime.utcnow().isoformat())
    )

db.commit()
print("Success!")
