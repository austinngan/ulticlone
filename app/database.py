import sqlite3
DB_FILE = "database.db"
db = sqlite3.connect(DB_FILE)
cur = db.cursor()

cur.execute("""
	CREATE TABLE IF NOT EXISTS users(
	  id INTEGER PRIMARY KEY,
	  username TEXT,
	  password TEXT)""")
	  
def fetch_user_id(username, password):

	db = sqlite3.connect(DB_FILE)

	db.row_factory = lambda curr, row: row[0]
	c = db.cursor()

	c.execute("""
		SELECT id
		FROM   users
		WHERE  LOWER(username) = LOWER(?)
		AND    password = ?
	""", (username, password))

	# user_id is None if no matches were found
	user_id = c.fetchone()

	db.close()

	return user_id

def register_user(username, password):

	db = sqlite3.connect(DB_FILE)
	c = db.cursor()

	c.execute("SELECT * FROM users WHERE LOWER(username) = LOWER(?)", (username,))
	row = c.fetchone()

	if row is not None:
		return False

	c.execute("""INSERT INTO users(username,password) VALUES(?, ?)""",(username,password))
	db.commit()
	db.close()
	return True


def fetch_username(user_id):

	db = sqlite3.connect(DB_FILE)
	db.row_factory = lambda curr, row: row[0]
	c = db.cursor()

	c.execute("SELECT username FROM users WHERE id = ?", (user_id,))
	username = c.fetchone()

	db.close()
	return username
