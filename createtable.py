import sqlite3

# Connect to the SQLite database
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# Define the CREATE TABLE statement
create_table_sql = """
CREATE TABLE IF NOT EXISTS "productlist" (
    "Source_Link"    TEXT,
    "Title"    TEXT,
    "Original_Price"    TEXT,
    "Current_Price"    TEXT,
    "Product_Link"    TEXT UNIQUE,
    "Image_Link"    TEXT,
    "timestamp"    DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY("Product_Link")
);
"""

# Execute the CREATE TABLE statement
cursor.execute(create_table_sql)
conn.commit()
# Close the connection
conn.close()