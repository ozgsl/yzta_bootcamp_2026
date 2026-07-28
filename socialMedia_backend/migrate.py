import sqlite3

def run():
    conn = sqlite3.connect('dijital_gardrop.db')
    c = conn.cursor()
    
    try:
        c.execute('ALTER TABLE kiyafetler ADD COLUMN is_favorite INTEGER NOT NULL DEFAULT 0;')
        print("Added is_favorite column.")
    except Exception as e:
        print("is_favorite column might already exist:", e)

    try:
        c.execute('''
        CREATE TABLE IF NOT EXISTS notifications (
            notification_id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            actor_id TEXT NOT NULL,
            type TEXT NOT NULL,
            post_id TEXT DEFAULT NULL,
            content TEXT DEFAULT NULL,
            is_read INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
            FOREIGN KEY (actor_id) REFERENCES users(user_id) ON DELETE CASCADE,
            FOREIGN KEY (post_id) REFERENCES posts(post_id) ON DELETE CASCADE
        );
        ''')
        c.execute('CREATE INDEX IF NOT EXISTS idx_notifications_user ON notifications(user_id, created_at DESC);')
        print("Created notifications table.")
    except Exception as e:
        print("Failed to create notifications table:", e)
        
    conn.commit()
    conn.close()

if __name__ == "__main__":
    run()
