import sqlite3

# Step 1: Connect to SQLite database (or create it if it doesn't exist)
db_name = 'database.db'
conn = sqlite3.connect(db_name)

# Step 2: Create a cursor object using the connection
cursor = conn.cursor()

# Step 3: Write the SQL query to create a table if it doesn't exist
create_table_query = '''
CREATE TABLE IF NOT EXISTS hearing_test (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    age INTEGER NOT NULL,
    volume INTEGER NOT NULL
);
'''

# Step 4: Execute the query to create the table
cursor.execute(create_table_query)

# Step 5: Commit the transaction and close the connection
conn.commit()
conn.close()

print(f"Database '{db_name}' created with 'hearing_test' table.")
