
import sqlite3


def create_database():
    connection = sqlite3.connect("ingestion.db")

    connection.execute("""
        CREATE TABLE IF NOT EXISTS ingestion_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            message TEXT NOT NULL,
            intent TEXT NOT NULL,
            risk_profile TEXT NOT NULL,
            priority INTEGER NOT NULL,
            summary TEXT NOT NULL,
            input_tokens INTEGER NOT NULL
        )
    """)

    connection.commit()
    connection.close()


def save_record(message, intent, risk_profile, priority, summary, input_tokens):
    connection = sqlite3.connect("ingestion.db")

    connection.execute("""
        INSERT INTO ingestion_records
        (message, intent, risk_profile, priority, summary, input_tokens)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (message, intent, risk_profile, priority, summary, input_tokens))

    connection.commit()
    connection.close()


if __name__ == "__main__":
    create_database()
    print("Database created successfully!")
