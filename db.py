import os
import mysql.connector

# Credentials are read from environment variables first so you're not
# committing a real password to source control. If the env var isn't set,
# it falls back to your existing local values.
connection = mysql.connector.connect(
    host=os.getenv("DEN_DB_HOST", "localhost"),
    user=os.getenv("DEN_DB_USER", "root"),
    password=os.getenv("DEN_DB_PASSWORD", "Pratham@2007"),
    database=os.getenv("DEN_DB_NAME", "den_sys")
)

cursor = connection.cursor(buffered=True)
