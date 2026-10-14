
import sqlite3

connection = sqlite3.connect("ingestion.db")

cursor = connection.cursor()

cursor.execute("SELECT * FROM ingestion_records")

records = cursor.fetchall()

if records:
    print("Database records found:\n")

    for record in records:
        print("ID:", record[0])
        print("Message:", record[1])
        print("Intent:", record[2])
        print("Risk Profile:", record[3])
        print("Priority:", record[4])
        print("Summary:", record[5])
        print("Input Tokens:", record[6])
        print("-" * 40)
else:
    print("No records found in the database.")

connection.close()
