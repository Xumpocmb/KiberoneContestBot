import sqlite3

conn = sqlite3.connect("bot_database.db")
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS participants (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    fio TEXT NOT NULL,
    video_filename TEXT NOT NULL,
    video_file_id TEXT NOT NULL,
    likes INTEGER DEFAULT 0,
    has_voted BOOLEAN DEFAULT 0
)''')
conn.commit()