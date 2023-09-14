import sqlite3

# Connect to the SQLite database
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# Check if the table "productlist" already exists
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='productlist'")
table_exists = cursor.fetchone()

if not table_exists:
    # The table does not exist, so create it
    cursor.execute('''
    CREATE TABLE "productlist" (
        "Source_Link" TEXT,
        "Title" TEXT,
        "Original_Price" TEXT,
        "Current_Price" TEXT,
        "Product_Link" TEXT UNIQUE,
        "Image_Link" TEXT,
        PRIMARY KEY("Product_Link")
    )''')
    # Commit the changes
    conn.commit()

# Close the connection
conn.close()