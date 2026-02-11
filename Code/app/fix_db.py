import sqlite3

# Connect to your existing database
conn = sqlite3.connect('users.db')
c = conn.cursor()

try:
    # Attempt to add the new columns safely
    c.execute("ALTER TABLE history ADD COLUMN cost TEXT")
    c.execute("ALTER TABLE history ADD COLUMN acres TEXT")
    print("✅ SUCCESS: Added 'cost' and 'acres' columns to your Database.")
except sqlite3.OperationalError:
    print("ℹ️ NOTE: Columns already exist. No changes needed.")

conn.commit()
conn.close()