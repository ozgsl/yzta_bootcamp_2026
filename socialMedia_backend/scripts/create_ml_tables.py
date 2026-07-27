import sqlite3
conn = sqlite3.connect('dijital_gardrop.db')
with open('../ML_repo_Ahmet/database.py', 'r', encoding='utf-8') as f:
    code = f.read()
import re
matches = re.findall(r'CREATE TABLE IF NOT EXISTS [\s\S]+?\)', code)
for match in matches:
    try:
        conn.execute(match)
        print('Created table from match:', match.split('(')[0])
    except Exception as e:
        print('Error:', e, match)
conn.commit()
conn.close()
