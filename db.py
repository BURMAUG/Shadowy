import sqlite3

# ======================= DATABASE CONFIG ==============================================
connection = sqlite3.connect('/Users/dj/Desktop/job_db.repository')
# connection = sqlite3.connect('/app/db/job_db.repository')
cursor = connection.cursor()

cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS job_db(
    id INTEGER PRIMARY KEY,
    company_name TEXT,
    position TEXT,
    posted INTEGER check ( posted <= 8 ))
    """
)
