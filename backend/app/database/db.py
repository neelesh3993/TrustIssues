import sqlite3
import json
from pathlib import Path
from datetime import datetime

DB_PATH = Path("screenshield.db")


def get_connection():
    return sqlite3.connect(DB_PATH)


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS scans (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        input_text TEXT UNIQUE,
        response_json TEXT,
        created_at TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()


def save_scan(text: str, response: dict):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT OR REPLACE INTO scans (input_text, response_json, created_at)
    VALUES (?, ?, ?)
    """, (text, json.dumps(response), datetime.utcnow()))

    conn.commit()
    conn.close()


def get_cached_scan(text: str):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT response_json FROM scans
    WHERE input_text = ?
    """, (text,))

    result = cursor.fetchone()
    conn.close()

    if result:
        return json.loads(result[0])
    return None
