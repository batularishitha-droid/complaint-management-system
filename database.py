import sqlite3

conn=sqlite3.connect("complaints.db",check_same_thread=False)
cursor=conn.cursor()

def create_table():

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS complaints(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticket TEXT,
    student_name TEXT,
    student_id TEXT,
    student_email TEXT,
    department TEXT,
    section TEXT,
    complaint_for TEXT,
    category TEXT,
    issue TEXT,
    description TEXT,
    image BLOB,
    priority TEXT,
    status TEXT DEFAULT 'Pending',
    feedback TEXT,
    rating TEXT,
    date_created TEXT
    )
    """)

    # Add student_email column if it doesn't exist (for existing databases)
    try:
        cursor.execute("ALTER TABLE complaints ADD COLUMN student_email TEXT")
    except sqlite3.OperationalError:
        pass  # Column already exists

    conn.commit()


def add_complaint(data):

    cursor.execute("""
    INSERT INTO complaints
    (ticket,student_name,student_id,student_email,department,section,complaint_for,category,issue,description,image,priority,status,feedback,rating,date_created)
    VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """,data)

    conn.commit()


def get_all_complaints():

    cursor.execute("SELECT * FROM complaints")

    return cursor.fetchall()


def get_category_complaints(category):

    cursor.execute("SELECT * FROM complaints WHERE category=?",(category,))

    return cursor.fetchall()


def get_student_complaints(student_id):

    cursor.execute("SELECT * FROM complaints WHERE student_id=?", (student_id,))

    return cursor.fetchall()


def get_complaint_by_id(cid):

    cursor.execute("SELECT * FROM complaints WHERE id=?", (cid,))

    return cursor.fetchone()


def update_status(cid,status):

    cursor.execute("UPDATE complaints SET status=? WHERE id=?",(status,cid))

    conn.commit()


def get_complaint_counts():

    cursor.execute("SELECT status, COUNT(*) FROM complaints GROUP BY status")

    return dict(cursor.fetchall())