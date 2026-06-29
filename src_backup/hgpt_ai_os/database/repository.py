from .engine import DatabaseEngine


class Repository:
    def __init__(self, engine: DatabaseEngine):
        self.engine = engine

    def create_user(self, username, fullname, role):
        self.engine.execute(
            """
            INSERT INTO users(username, fullname, role)
            VALUES (?, ?, ?)
            """,
            (username, fullname, role),
        )

    def get_users(self):
        return self.engine.fetchall(
            "SELECT * FROM users ORDER BY id"
        )

    def get_user(self, user_id):
        return self.engine.fetchone(
            "SELECT * FROM users WHERE id=?",
            (user_id,),
        )

    def update_user(self, user_id, fullname, role):
        self.engine.execute(
            """
            UPDATE users
            SET fullname=?, role=?
            WHERE id=?
            """,
            (fullname, role, user_id),
        )

    def delete_user(self, user_id):
        self.engine.execute(
            "DELETE FROM users WHERE id=?",
            (user_id,),
        )