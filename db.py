import mysql.connector

connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Pratham@2007",
    database="den_sys"
)

cursor = connection.cursor()