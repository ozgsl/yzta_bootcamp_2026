import sqlite3

def run():
    with open('schema.sql', 'r', encoding='utf-8') as f:
        schema = f.read()
    conn = sqlite3.connect('dijital_gardrop.db')
    conn.executescript(schema)
    conn.commit()
    conn.close()
    print("Schema applied successfully!")

if __name__ == '__main__':
    run()
