import sqlite3
import random
import string

# Connection to the db
conn = sqlite3.connect('apache_airlines.db')
cursor = conn.cursor()

# Create bookings table with seat uniqueness constraint
cursor.execute('''
    CREATE TABLE IF NOT EXISTS bookings (
        booking_ref TEXT PRIMARY KEY,
        passport TEXT,
        first_name TEXT,
        last_name TEXT,
        seat TEXT UNIQUE,  -- Prevents double bookings
        price INTEGER  
    )
''')
conn.commit()

SEAT_PRICES = {
    "window": 50,   # Columns A/F
    "aisle": 40,    # Columns C/D
    "middle": 30    # Columns B/E
}

storage_seats = {"77D", "77E", "77F", "78D", "78E", "78F"}
seats = {f"{row}{col}" for row in range(1, 81) for col in "ABCDEF"}


# Function that determines seat type based on column letter
def get_seat_type(seat):
    col = seat[-1]
    return "window" if col in ("A", "F") else \
           "aisle" if col in ("C", "D") else \
           "middle" if col in ("B", "E") else None

# Function that generates unique 8-character alphanumeric references.

def generate_booking_ref():
    while True:
        ref = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        cursor.execute('SELECT 1 FROM bookings WHERE booking_ref = ?', (ref,))
        if not cursor.fetchone():
            return ref


# Function that checks whether a seat is booked or not.
def check_availability():
    while True:
        seat = input("\nEnter seat (e.g., 1A): ").upper()
        if seat not in seats:
            print("Invalid seat! Use format like 1A-80F.")
            continue
        
        if seat in storage_seats:
            print(f"Seat {seat}: Storage Area (Not Bookable)")
            break
        
        # Check database for booking
        cursor.execute('SELECT 1 FROM bookings WHERE seat = ?', (seat,))
        if cursor.fetchone():
            print(f"Seat {seat}: Reserved")
        else:
            seat_type = get_seat_type(seat)
            price = SEAT_PRICES[seat_type]
            print(f"Seat {seat}: Available ({seat_type} seat - ${price})")
        break

# Function to book a seat, it checks if the seat is booked in the database.
def book_seat():
    # Check if airplane is fully booked
    cursor.execute('SELECT COUNT(*) FROM bookings')
    booked_count = cursor.fetchone()[0]
    max_capacity = len(seats) - len(storage_seats)  # Total bookable seats
    
    if booked_count >= max_capacity:
        print("\nAirplane is fully booked. No seats available.")
        return  # Exit function early

    # Proceed with booking if seats are available
    while True:
        seat = input("\nEnter seat to book (Window: 50$, Aisle: 40$, Middle: 30$) (eg. 1F): ").upper()
        
        # Validate seat
        if seat not in seats:
            print("Invalid seat number.")
            continue
        if seat in storage_seats:
            print("Cannot book storage area.")
            continue
        
        # Check if already booked
        cursor.execute('SELECT 1 FROM bookings WHERE seat = ?', (seat,))
        if cursor.fetchone():
            print("Seat already booked.")
            continue
        
        # Get passenger details
        passport = input("Passport number: ").strip()
        first = input("First name: ").strip().title()
        last = input("Last name: ").strip().title()
        price = SEAT_PRICES[get_seat_type(seat)]
        confirm = input(f"Price: ${price} ({get_seat_type(seat)} seat). Confirm? (Y/N): ").upper()
        
        if confirm == "N":
            break
        # Generate reference and save to DB
        ref = generate_booking_ref()
        cursor.execute('''
            INSERT INTO bookings 
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (ref, passport, first, last, seat, price))
        conn.commit()
        print(f"Booked {seat}! Reference: {ref}")
        break
        

            
#Function that frees a seat, ultimately canceling a booking            
def free_seat():
    while True:
        seat = input("\nEnter seat to free: ").upper()
        
        # Delete from database
        cursor.execute('DELETE FROM bookings WHERE seat = ?', (seat,))
        if cursor.rowcount == 0:
            print("Seat not booked or invalid.")
            continue
        
        conn.commit()
        print(f"Freed {seat} successfully.")
        break

# Function that shows the booking status of a customer, and prints the seating plan
def show_booking_status():
    # Get passenger's full name
    first_name = input("\nEnter your first name: ").strip().title()
    last_name = input("Enter your last name: ").strip().title()
    
    # Query database for bookings
    cursor.execute('''
        SELECT booking_ref, seat, price 
        FROM bookings 
        WHERE first_name = ? AND last_name = ?
    ''', (first_name, last_name))
    bookings = cursor.fetchall()
    
    # Display booking information
    if not bookings:
        print(f"\nNo bookings found for '{first_name} {last_name}'.")
    else:
        print(f"\n{'+++++++++ Your Bookings +++++++++'}")
        for idx, (ref, seat, price) in enumerate(bookings, 1):
            print(f"{idx}. Reference: {ref}")
            print(f"   First Name: {first_name}")
            print(f"   Last Name:  {last_name}")
            print(f"   Seat: {seat}")
            print(f"   Price: ${price}\n")
    
    # Display full seat map
    print("\nCurrent Floor Plan of Burak757:")
    cursor.execute('SELECT seat FROM bookings')
    taken_seats = {row[0] for row in cursor.fetchall()}
    
    for row in range(1, 81):  # Rows 1-80
        row_display = []
        for col in "ABCXDEF":  # Columns A-F with aisle (X)
            seat = f"{row}{col}"
            
            # Determine what to display
            if col == "X":
                display = " X"  # Aisle
            elif seat in taken_seats:
                display = "R"  # Booked
            elif seat in storage_seats:
                display = "S"  # Storage
            else:
                display = seat  # Available seat

            # Format to 4-character width for alignment
            row_display.append(f"{display:<4}")  # Left-aligned, 4 chars
            
        print("".join(row_display))  # Print entire row

# Menu System that is ran at every iteration 
def menu():
    print("\n| Apache Airlines Booking System |")
    print("1. Check availability of seat")
    print("2. Book a seat")
    print("3. Free a seat")
    print("4. Show booking status")
    print("5. Exit")

#  Main Loop 
while True:
    menu()
    choice = input("Choose option (1-5): ").strip()
    
    if choice == "1":
        check_availability()
    elif choice == "2":
        book_seat()
    elif choice == "3":
        free_seat()
    elif choice == "4":
        show_booking_status()
    elif choice == "5":
        print("Exiting Program")
        conn.close()
        break
    else:
        print("Invalid choice. Try again.")
