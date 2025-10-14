import sqlite3
import os
from werkzeug.security import generate_password_hash

db_path = os.path.join(os.path.dirname(__file__), 'LoginData.db')
connection = sqlite3.connect(db_path)
cursor = connection.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS USERS(
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    email VARCHAR(50) PRIMARY KEY,
    password VARCHAR(255) NOT NULL,
    academic_year TEXT CHECK(academic_year IN ('freshman','sophomore','junior','senior','grad')),
    age INTEGER,
    country TEXT,
    avatar_seed TEXT
)
""")

hashed_password = generate_password_hash('tester', method='pbkdf2:sha256', salt_length=8)

cursor.execute("""
INSERT OR IGNORE INTO USERS(first_name, last_name, email, password, academic_year, age, country, avatar_seed)
VALUES ('tester', 'tester', 'tester@gmail.com', ?, 'junior', 21, 'Cyprus', 'tester@gmail.com')
""", (hashed_password,))

hashed_password_fanta = generate_password_hash('fanta123', method='pbkdf2:sha256', salt_length=8)
cursor.execute("""
INSERT OR IGNORE INTO USERS(first_name, last_name, email, password, academic_year, age, country, avatar_seed)
VALUES ('Fanta', 'Girl', 'fanta@gmail.com', ?, 'sophomore', 20, 'Cyprus', 'fanta@gmail.com')
""", (hashed_password_fanta,))

hashed_password_wassa = generate_password_hash('wassa123', method='pbkdf2:sha256', salt_length=8)
cursor.execute("""
INSERT OR IGNORE INTO USERS(first_name, last_name, email, password, academic_year, age, country, avatar_seed)
VALUES ('Wassa', 'Girl', 'wassa@gmail.com', ?, 'junior', 21, 'Cyprus', 'wassa@gmail.com')
""", (hashed_password_wassa,))

hashed_password_emman = generate_password_hash('emman123', method='pbkdf2:sha256', salt_length=8)

cursor.execute("""
INSERT OR IGNORE INTO USERS(first_name, last_name, email, password, academic_year, age, country, avatar_seed)
VALUES ('Emman', 'Test', 'bluebericollection@gmail.com', ?, 'senior', 25, 'Ethiopia', 'bluebericollection@gmail.com')
""", (hashed_password_emman,))

cursor.execute("""
CREATE TABLE IF NOT EXISTS ROOMMATE_PREFERENCES(
    email VARCHAR(50) PRIMARY KEY,
    cleanliness VARCHAR(10),
    study_habits VARCHAR(10),
    sleep_schedule VARCHAR(10),
    social_habits VARCHAR(10),
    noise_tolerance VARCHAR(10),
    guests VARCHAR(10),
    smoking_drinking VARCHAR(10),
    FOREIGN KEY(email) REFERENCES USERS(email)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS MESSAGES(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sender VARCHAR(50),
    receiver VARCHAR(50),
    content TEXT,
    timestamp DATETIME DEFAULT (datetime('now','localtime')),
    FOREIGN KEY(sender) REFERENCES USERS(email),
    FOREIGN KEY(receiver) REFERENCES USERS(email)
)
""")
connection.commit()

users = cursor.execute("SELECT * FROM USERS").fetchall()
print("USERS:", users)

connection.close()
