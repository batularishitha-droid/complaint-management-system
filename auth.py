import sqlite3

conn=sqlite3.connect("complaints.db",check_same_thread=False)
cursor=conn.cursor()

def create_users():

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users(
    username TEXT PRIMARY KEY,
    password TEXT,
    role TEXT)
    """)

    conn.commit()


def register(username,password,role):

    cursor.execute("SELECT * FROM users WHERE username=?",(username,))
    user=cursor.fetchone()

    if user:
        return False,"Username already exists"

    cursor.execute("INSERT INTO users VALUES(?,?,?)",(username,password,role))

    conn.commit()

    return True,"Registration Successful"


def login(username,password):

    cursor.execute("SELECT username,role FROM users WHERE username=? AND password=?",
                   (username,password))

    return cursor.fetchone()


def get_all_admins():

    cursor.execute("""
        SELECT username, role
        FROM users
        WHERE role != 'Student'
        ORDER BY role
    """)

    return cursor.fetchall()