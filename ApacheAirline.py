import sqlite3
import random
import string
import tkinter as tk # the tkinter library for GUI
from tkinter import font as tkFont # For GUI font control

# Connection to the db
conn = sqlite3.connect('apache_airlines.db')
cursor = conn.cursor()
TOTAL_ROWS = 80
AISLE_COL_INDEX = 3 
SEAT_COLS = "ABCDEF"

#  Colors for GUI 
COLOR_AVAILABLE = "lightgrey"
COLOR_RESERVED = "red"
COLOR_STORAGE = "lightblue"
COLOR_AISLE = "white"
COLOR_TEXT_AVAILABLE = "black"
COLOR_TEXT_RESERVED = "white"
COLOR_TEXT_STORAGE = "black"

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
        seat = input("\nEnter seat (e.g., 1A) or * for main menu:").upper()
        if seat == "*":
            return
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
        show_booking_display()
        seat = input("\nEnter seat to book (Window: 50$, Aisle: 40$, Middle: 30$) (eg. 1F) or * for main menu: ").upper()
        if seat == "*":
            return  
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
        passport = input("Passport number: ").strip().upper()
        first = input("First name: ").strip().title()
        last = input("Last name: ").strip().title()
        price = SEAT_PRICES[get_seat_type(seat)]
        confirm = input(f"Price: ${price} ({get_seat_type(seat)} seat). Confirm? (Y/N): ").upper()
        
        if confirm == "Y":
            ref = generate_booking_ref()
            cursor.execute('''
                INSERT INTO bookings 
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (ref, passport, first, last, seat, price))
            conn.commit()
            print(f"Booked {seat}! Reference: {ref}")
            show_booking_display()
            break
        else:
            print("No Booking Made")
            return;

            
#Function that frees a seat, ultimately canceling a booking            
def free_seat():
    while True:
        show_booking_display()
        seat = input("\nEnter seat to free (e.g., 1A) or * for main menu: ").upper().strip()
        if (seat == "*"):
            return
        last_name = input("Enter your last name: ").strip().title()  # Format name
        passport = input("Enter your passport number: ").strip().upper()
        
        # delete with authentication
        cursor.execute('''
            DELETE FROM bookings 
            WHERE seat = ? 
            AND UPPER(last_name) = UPPER(?) 
            AND passport = ?
        ''', (seat, last_name, passport))
        
        if cursor.rowcount == 0:
            print("No booking found matching:")
            print(f"- Seat: {seat}")
            print(f"- Last Name: {last_name}")
            print(f"- Passport: {passport}\n")
            break
        
        conn.commit()
        show_booking_display()
        print(f"Successfully freed seat {seat}!")
        break
# Function that shows the booking status of a customer, and prints the GUI seating plan
def show_booking_status():

    # Get passenger's full name for console output
    first_name = input("\nEnter your first name: ").strip().title()
    last_name = input("Enter your last name: ").strip().title()

    if not first_name or not last_name:
        print("First and Last name empty, continuing.")
        

    # Query database for specific passenger bookings
    cursor.execute('''
        SELECT booking_ref, seat, price, passport
        FROM bookings
        WHERE first_name = ? AND last_name = ?
    ''', (first_name, last_name))
    bookings = cursor.fetchall()

    # Display booking information in CONSOLE
    print("-" * 40) # Separator
    if not bookings:
        print(f"No bookings found for '{first_name} {last_name}'.")
    else:
        print(f"Booking Details for: {first_name} {last_name}")
        for idx, (ref, seat, price, passport) in enumerate(bookings, 1):
            print(f"  Booking {idx}:")
            print(f"    Reference: {ref}")
            print(f"    Seat:      {seat}")
            print(f"    Price:     ${price}")
            print(f"    Passport:  {passport}") 
            print("-" * 20) # Separator between multiple bookings for same person
    print("-" * 40) # Separator
    show_booking_display()

def show_booking_display():
      # Prepare for GUI Map 
    # Display full seat map title in CONSOLE
    print("\nLoading Seat Map...")

    # Fetch ALL currently booked seats for the map
    cursor.execute('SELECT seat FROM bookings')
    # Create a set of booked seats for efficient lookup in the GUI part
    taken_seats = {row[0] for row in cursor.fetchall()}

    # GUI Map Display 
    gui_root = tk.Tk()
    gui_root.title("Apache Airlines Seat Map")
    gui_root.geometry("450x650") 

    # legend Frame 
    legend_frame = tk.Frame(gui_root, pady=5)
    legend_frame.pack(side=tk.TOP, fill=tk.X)
    # Create small colored squares for the legend visually
    tk.Label(legend_frame, text="Legend:", anchor='w').pack(side=tk.LEFT, padx=5)
    tk.Label(legend_frame, text="Avail", bg=COLOR_AVAILABLE, fg=COLOR_TEXT_AVAILABLE, relief=tk.RIDGE, borderwidth=1, width=4).pack(side=tk.LEFT, padx=2)
    tk.Label(legend_frame, text="X", bg=COLOR_AVAILABLE, fg=COLOR_TEXT_AVAILABLE, relief=tk.RIDGE, borderwidth=1, width=4).pack(side=tk.LEFT, padx=2)
    tk.Label(legend_frame, text="R", bg=COLOR_RESERVED, fg=COLOR_TEXT_RESERVED, relief=tk.RIDGE, borderwidth=1, width=4).pack(side=tk.LEFT, padx=2)
    tk.Label(legend_frame, text="S", bg=COLOR_STORAGE, fg=COLOR_TEXT_STORAGE, relief=tk.RIDGE, borderwidth=1, width=4).pack(side=tk.LEFT, padx=2)


    # Seat Map Frame and  Canvas for scrolling
    canvas = tk.Canvas(gui_root)
    scrollbar = tk.Scrollbar(gui_root, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas)

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    # Create Seat Layout in the scrollable_frame 
    seat_font = tkFont.Font(size=8) # Smaller font for seats
    label_width = 5 # Width of seat labels
    label_height = 1 # Height of seat labels

    # Create Header Row (Row, A, B, C, , D, E, F)
    header_cols = list(SEAT_COLS[:AISLE_COL_INDEX]) + ['X'] + list(SEAT_COLS[AISLE_COL_INDEX:]) # Use space for visual aisle
    tk.Label(scrollable_frame, text="Row", width=3, relief=tk.GROOVE).grid(row=0, column=0, padx=1, pady=1)
    for col_idx, col_letter in enumerate(header_cols):
        header_label = tk.Label(scrollable_frame, text=col_letter, width=label_width if col_letter != ' ' else label_width//2, font=seat_font, relief=tk.GROOVE)
        header_label.grid(row=0, column=col_idx + 1, padx=1 if col_letter != ' ' else 0, pady=1) # Offset by 1 for row number col


    # Create Seat Grid
    for gui_row in range(1, TOTAL_ROWS + 1): # GUI row matches actual row number
        # Add Row Number Label
        row_num_label = tk.Label(scrollable_frame, text=str(gui_row), width=3, relief=tk.GROOVE)
        row_num_label.grid(row=gui_row, column=0, padx=1, pady=1, sticky='ew') # Place row number in first col

        gui_col_index = 1 # Start seats from the second GUI column

        for idx, seat_char in enumerate(SEAT_COLS): # A, B, C, D, E, F
            if idx == AISLE_COL_INDEX : # Insert visual aisle space
                aisle_label = tk.Label(scrollable_frame, text="X", bg=COLOR_AISLE, width=label_width , height=label_height) 
                aisle_label.grid(row=gui_row, column=gui_col_index, padx=0, pady=1, sticky='ns')
                gui_col_index += 1

            seat_id = f"{gui_row}{seat_char}"
            bg_color = COLOR_AVAILABLE
            fg_color = COLOR_TEXT_AVAILABLE
            seat_text = seat_id

            # Use the taken_seats set fetched from DB earlier
            if seat_id in taken_seats:
                bg_color = COLOR_RESERVED
                fg_color = COLOR_TEXT_RESERVED
                seat_text = "R" # Show 'R' for reserved
            elif seat_id in storage_seats:
                bg_color = COLOR_STORAGE
                fg_color = COLOR_TEXT_STORAGE
                seat_text = "S" # Show 'S' for storage
            # else: seat is available, defaults are set above

            # Create the seat label
            seat_label = tk.Label(scrollable_frame, text=seat_text, bg=bg_color, fg=fg_color,
                                  width=label_width, height=label_height, font=seat_font, relief=tk.RIDGE, borderwidth=1)
            seat_label.grid(row=gui_row, column=gui_col_index, padx=1, pady=1)
            gui_col_index += 1


    # Starting the Tkinter event loop - this displays the window
    print("Displaying graphical seat map...") # Inform user GUI is opening
    gui_root.mainloop()
    print("Seat map window closed.") # Inform user GUI is closed
    
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
