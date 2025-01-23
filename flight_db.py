# flight_db.py
import sqlite3
from datetime import datetime

class DatabaseManager:
    def __init__(self, db_name='Flight_Management_Database.db'):
        self.db_name = db_name
        self._init_database()
    
    def _init_database(self):
        with sqlite3.connect(self.db_name) as conn:
            cur = conn.cursor()
            
            cur.execute("""
                CREATE TABLE IF NOT EXISTS pilots (
                    pilot_id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    license_num TEXT UNIQUE,
                    rating TEXT,
                    hours_logged INTEGER
                )
            """)
            
            cur.execute("""
                CREATE TABLE IF NOT EXISTS destinations (
                    dest_id INTEGER PRIMARY KEY,
                    airport_code TEXT UNIQUE,
                    city TEXT,
                    country TEXT,
                    gates INTEGER,
                    status TEXT
                )
            """)
            
            cur.execute("""
                CREATE TABLE IF NOT EXISTS flights (
                    flight_id INTEGER PRIMARY KEY,
                    flight_code TEXT UNIQUE,
                    departure TEXT,
                    arrival TEXT,
                    aircraft_type TEXT,
                    pilot_id INTEGER,
                    dest_id INTEGER,
                    status TEXT,
                    FOREIGN KEY (pilot_id) REFERENCES pilots(pilot_id),
                    FOREIGN KEY (dest_id) REFERENCES destinations(dest_id)
                )
            """)