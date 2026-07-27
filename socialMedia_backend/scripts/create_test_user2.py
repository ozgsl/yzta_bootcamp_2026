import sqlite3
import uuid
import datetime
import random

db = sqlite3.connect('database.db')

# Get testuser's password hash so we don't have to rehash with passlib and crash
test_hash = db.execute('SELECT password_hash FROM users WHERE email=?', ('testuser@gmail.com',)).fetchone()[0]

user_id = str(uuid.uuid4())
username = 'yenitest'
email = 'yenitest@gmail.com'
password = 'testuser123'
display_name = 'Yeni Test Kullanicisi'

# Insert user
db.execute('INSERT INTO users (user_id, username, email, password_hash, display_name, created_at) VALUES (?, ?, ?, ?, ?, ?)',
    (user_id, username, email, test_hash, display_name, datetime.datetime.utcnow().isoformat() + 'Z'))

# Insert posts
for i in range(3):
    post_id = str(uuid.uuid4())
    image_url = 'https://picsum.photos/400/500?random=' + str(random.randint(1000, 9999))
    caption = f'Benim yeni postum #{i+1}'
    db.execute('INSERT INTO posts (post_id, user_id, image_url, caption, created_at) VALUES (?, ?, ?, ?, ?)',
        (post_id, user_id, image_url, caption, datetime.datetime.utcnow().isoformat() + 'Z'))

# Create saved_posts table if not exists (just in case)
db.execute('''
    CREATE TABLE IF NOT EXISTS saved_posts (
        user_id   TEXT NOT NULL,
        post_id   TEXT NOT NULL,
        saved_at  TEXT NOT NULL,
        PRIMARY KEY (user_id, post_id)
    )
''')

# Save other posts
other_posts = db.execute('SELECT post_id FROM posts WHERE user_id != ? LIMIT 5', (user_id,)).fetchall()
for p in other_posts:
    db.execute('INSERT OR IGNORE INTO saved_posts (user_id, post_id, saved_at) VALUES (?, ?, ?)',
        (user_id, p[0], datetime.datetime.utcnow().isoformat() + 'Z'))

db.commit()
print('SUCCESS')
