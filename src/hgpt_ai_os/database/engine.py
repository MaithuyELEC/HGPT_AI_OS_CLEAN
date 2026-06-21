from pathlib import Path
import sqlite3


class DatabaseEngine:
    def __init__(self, db_name="hgpt_ai_os.db"):
        db_dir = Path("database")
        db_dir.mkdir(exist_ok=True)

        self.db_path = db_dir / db_name
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()

    def execute(self, sql, params=()):
        self.cursor.execute(sql, params)
        self.conn.commit()

    def fetchone(self, sql, params=()):
        self.cursor.execute(sql, params)
        return self.cursor.fetchone()

    def fetchall(self, sql, params=()):
        self.cursor.execute(sql, params)
        return self.cursor.fetchall()

    def close(self):
        self.conn.close()