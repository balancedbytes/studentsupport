import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), 'LoginData.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("SELECT * FROM ROOMMATE_PREFERENCES")
rows = cursor.fetchall()
for row in rows:
    print(row)

conn.close()
