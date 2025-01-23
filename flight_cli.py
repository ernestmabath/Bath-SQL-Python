# flight_cli.py
import sqlite3
from tabulate import tabulate
from flight_db import DatabaseManager

class FlightManager:
    def __init__(self, db_name='Flight_Management_Database.db'):
        self.conn = sqlite3.connect(db_name)
        self.cur = self.conn.cursor()
        
    def add_flight(self):
        try:
            print("\n=== Add New Flight ===")
            flight_data = {
                'code': input("Flight code (X####): "),
                'dep': input("Departure (YYYYMMDD HHMM): "),
                'arr': input("Arrival (YYYYMMDD HHMM): "),
                'dest': input("Destination: "),
                'aircraft': input("Aircraft type: "),
                'status': 'Scheduled'
            }
            
            # First, get or insert destination
            self.cur.execute("""
                INSERT OR IGNORE INTO destinations (city)
                VALUES (?)
            """, (flight_data['dest'],))
            
            # Get the destination ID
            self.cur.execute("""
                SELECT dest_id FROM destinations
                WHERE city = ?
            """, (flight_data['dest'],))
            dest_id = self.cur.fetchone()[0]
            
            # Insert flight with proper columns
            self.cur.execute("""
                INSERT INTO flights (
                    flight_code, departure, arrival, 
                    aircraft_type, dest_id, status
                )
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                flight_data['code'], 
                flight_data['dep'], 
                flight_data['arr'],
                flight_data['aircraft'],
                dest_id,
                flight_data['status']
            ))
            
            self.conn.commit()
            print("\nFlight added successfully")
            
        except sqlite3.IntegrityError:
            print("\nError: Flight code already exists")
        except Exception as e:
            print(f"\nError adding flight: {str(e)}")

    def view_flights(self):
        print("\n=== View Flights ===")
        print("1. View all flights")
        print("2. View by date")
        
        choice = input("\nSelect option (1-2): ")
        
        try:
            if choice == '1':
                self.cur.execute("""
                    SELECT f.flight_id, f.flight_code, f.departure, 
                        f.arrival, f.aircraft_type, f.pilot_id, 
                        d.city as destination, f.status
                    FROM flights f
                    LEFT JOIN destinations d ON f.dest_id = d.dest_id
                """)
            elif choice == '2':
                date = input("Enter date (YYYYMMDD): ")
                self.cur.execute("""
                    SELECT f.flight_id, f.flight_code, f.departure, 
                        f.arrival, f.aircraft_type, f.pilot_id, 
                        d.city as destination, f.status
                    FROM flights f
                    LEFT JOIN destinations d ON f.dest_id = d.dest_id
                    WHERE f.departure LIKE ?
                """, (f"{date}%",))
            else:
                print("Invalid option")
                return

            flights = self.cur.fetchall()
            if flights:
                headers = ['ID', 'Code', 'Departure', 'Arrival', 
                        'Aircraft', 'Pilot ID', 'Destination', 'Status']
                print(tabulate(flights, headers=headers, tablefmt='grid'))
            else:
                print("No flights found")
                
        except Exception as e:
            print(f"\nError viewing flights: {str(e)}")

    def update_flight(self):
        print("\n=== Update Flight ===")
        flight_code = input("Enter flight code to update (X####): ")
        
        print("\nWhat would you like to update?")
        print("1. Departure time")
        print("2. Arrival time")
        print("3. Aircraft type")
        print("4. Status")
            
        choice = input("\nSelect option (1-4): ")
        
        try:
            if choice == '1':
                new_value = input("New departure time (YYYYMMDD HHMM): ")
                field = 'departure'
            elif choice == '2':
                new_value = input("New arrival time (YYYYMMDD HHMM): ")
                field = 'arrival'
            elif choice == '3':
                new_value = input("New aircraft type: ")
                field = 'aircraft_type'
            elif choice == '4':
                new_value = input("New status: ")
                field = 'status'
            else:
                print("Invalid option")
                return

            self.cur.execute(f"""
                UPDATE flights 
                SET {field} = ?
                WHERE flight_code = ?
            """, (new_value, flight_code))
            
            if self.cur.rowcount > 0:
                self.conn.commit()
                print("\nFlight updated successfully")
            else:
                print("\nFlight not found")
                
        except Exception as e:
            print(f"\nError updating flight: {str(e)}")

    def assign_pilot(self):
        print("\n=== Assign Pilot to Flight ===")
        
        # Show available pilots
        self.cur.execute("SELECT pilot_id, name FROM pilots")
        pilots = self.cur.fetchall()
        print("\nAvailable pilots:")
        print(tabulate(pilots, headers=['ID', 'Name'], tablefmt='simple'))
        
        flight_code = input("\nEnter flight code: ")
        pilot_id = input("Enter pilot ID: ")
        
        try:
            self.cur.execute("""
                UPDATE flights 
                SET pilot_id = ?
                WHERE flight_code = ?
            """, (pilot_id, flight_code))
            
            if self.cur.rowcount > 0:
                self.conn.commit()
                print("\nPilot assigned successfully")
            else:
                print("\nFlight not found")
                
        except Exception as e:
            print(f"\nError assigning pilot: {str(e)}")

    def view_pilot_schedule(self):
        print("\n=== View Pilot Schedule ===")
        pilot_id = input("Enter pilot ID: ")
        
        try:
            self.cur.execute("""
                SELECT f.flight_code, f.departure, f.arrival,
                    d.city as destination, f.status
                FROM flights f
                LEFT JOIN destinations d ON f.dest_id = d.dest_id
                WHERE f.pilot_id = ?
                ORDER BY f.departure
            """, (pilot_id,))
            
            schedule = self.cur.fetchall()
            if schedule:
                headers = ['Flight', 'Departure', 'Arrival', 
                        'Destination', 'Status']
                print(tabulate(schedule, headers=headers, tablefmt='grid'))
            else:
                print("No flights scheduled for this pilot")
                
        except Exception as e:
            print(f"\nError viewing schedule: {str(e)}")

    def manage_destinations(self):
        print("\n=== Manage Destinations ===")
        print("1. View all destinations")
        print("2. Add new destination")
        print("3. Update destination")
        
        choice = input("\nSelect option (1-3): ")
        
        try:
            if choice == '1':
                self.cur.execute("""
                    SELECT * FROM destinations
                """)
                destinations = self.cur.fetchall()
                if destinations:
                    headers = ['ID', 'Airport Code', 'City', 'Country', 
                            'Gates', 'Status']
                    print(tabulate(destinations, headers=headers, 
                                tablefmt='grid'))
                else:
                    print("No destinations found")
                    
            elif choice == '2':
                dest_data = {
                    'code': input("Airport code: "),
                    'city': input("City: "),
                    'country': input("Country: "),
                    'gates': input("Number of gates: "),
                    'status': 'Active'
                }
                
                self.cur.execute("""
                    INSERT INTO destinations (airport_code, city, country, 
                                        gates, status)
                    VALUES (?, ?, ?, ?, ?)
                """, (dest_data['code'], dest_data['city'], 
                    dest_data['country'], dest_data['gates'], 
                    dest_data['status']))
                self.conn.commit()
                print("\nDestination added successfully")
                
            elif choice == '3':
                airport_code = input("Enter airport code to update: ")
                new_status = input("New status: ")
                
                self.cur.execute("""
                    UPDATE destinations 
                    SET status = ?
                    WHERE airport_code = ?
                """, (new_status, airport_code))
                
                if self.cur.rowcount > 0:
                    self.conn.commit()
                    print("\nDestination updated successfully")
                else:
                    print("\nDestination not found")
            else:
                print("Invalid option")
                
        except sqlite3.IntegrityError:
            print("\nError: Airport code already exists")
        except Exception as e:
            print(f"\nError managing destinations: {str(e)}")

    def close(self):
        self.conn.close()

def main():
    # Initialize database first
    db = DatabaseManager()
    
    # Create flight manager
    manager = FlightManager()
    
    menu_options = {
        '1': ('Add New Flight', manager.add_flight),
        '2': ('View Flights by Criteria', manager.view_flights),
        '3': ('Update Flight Information', manager.update_flight),
        '4': ('Assign Pilot to Flight', manager.assign_pilot),
        '5': ('View Pilot Schedule', manager.view_pilot_schedule),
        '6': ('Manage Destinations', manager.manage_destinations),
        '7': ('Exit', None)
    }
    
    while True:
        print("\n=== Flight Management System ===")
        for key, (label, _) in menu_options.items():
            print(f"{key}. {label}")
            
        choice = input("\nSelect option (1-7): ")
        
        if choice == '7':
            print("\nExiting system...")
            manager.close()
            break
        elif choice in menu_options:
            menu_options[choice][1]()
        else:
            print("\nInvalid option. Please try again.")

if __name__ == "__main__":
    main()