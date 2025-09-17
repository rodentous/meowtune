import sqlite3
import json


# Initialize database
def init_db():
    conn = sqlite3.connect("user_data.db")
    cursor = conn.cursor()
    cursor.execute(
        """
		CREATE TABLE IF NOT EXISTS users (
		user_id INTEGER PRIMARY KEY,
		state TEXT DEFAULT 'normal',
		preferences TEXT DEFAULT '{}',
		favorite_tracks TEXT DEFAULT ''
	)
	"""
    )
    conn.commit()
    conn.close()


def get_user_data(user_id):
    conn = sqlite3.connect("user_data.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()

    if user:
        return {
            "user_id": user[0],
            "state": user[1],
            "preferences": json.loads(user[2]),
            "favorite_tracks": user[3].split(","),
        }
    return user


def update_user_data(user_id, **updates):
    conn = sqlite3.connect("user_data.db")
    cursor = conn.cursor()

    if get_user_data(user_id):
        # Update existing user
        if len(updates.keys()) != 0:
            set_clause = ", ".join([f"{k} = ?" for k in updates.keys()])
            values = list(updates.values()) + [user_id]
            cursor.execute(f"UPDATE users SET {set_clause} WHERE user_id = ?", values)
    else:
        # Insert new user
        keys = ["user_id"] + list(updates.keys())
        placeholders = ", ".join(["?"] * len(keys))
        values = [user_id] + list(updates.values())
        cursor.execute(
            f'INSERT INTO users ({", ".join(keys)}) VALUES ({placeholders})', values
        )

    conn.commit()
    conn.close()
