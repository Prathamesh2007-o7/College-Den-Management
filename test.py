from db import cursor

cursor.execute("SELECT DATABASE();")

print(cursor.fetchone())