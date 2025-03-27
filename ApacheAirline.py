# seats that are being booked
taken_seats = {""}

# initial seating dictionary
seats = {f"{row}{col}": "F" for row in range(1, 81) for col in "ABCDEF"}

# Storage area seats
storage_seats = {"77D", "77E", "77F", "78D", "78E", "78F"}



# Seat pricing configuration
SEAT_PRICES = {
    "window": 50,   # Columns A and F
    "aisle": 40,    # Columns C and D 
    "middle": 30    # Columns B and E
}

#Function to determine the seat type given its letter
def get_seat_type(seat_number):
    column = seat_number[-1]  # Extracts column letter (like "1A" → "A")
    if column in ("A", "F"):
        return "window"
    elif column in ("C", "D"):
        return "aisle"
    elif column in ("B", "E"):
        return "middle"
    else:
        return None  
    
# Function that checks whether a seat is avaialable or not 
def check_availability():
    while True:
        seat = input("\nEnter seat number (e.g., 1A): ").upper()
        if seat in seats:
            if seat in taken_seats:
                print(f"Seat {seat}: Reserved")
            elif seat in storage_seats:
                print(f"Seat {seat}: Storage (Not Bookable)")
            else:
                seat_type = get_seat_type(seat)
                price = SEAT_PRICES[seat_type]
                print(f"Seat {seat}: Available ({seat_type.capitalize()} Seat - ${price})")
            break
        else:
            print("Invalid seat! Format must be 1A-80F. Try again.")
            
# Function that allows the user to book a seat as long as the plane isn't full yet.
def book_seat():
    total_seats = len(seats) - len(storage_seats)  # Total bookable seats
    if len(taken_seats) >= total_seats:
        print("\n Airplane is fully booked. No seats available.")
        return  
    while True:
        seat = input("\nEnter seat to book (Window: 50$, Aisle: 40$, Middle: 30$) (eg. 1F): ").upper()
        if seat not in seats:
            print("Invalid seat number. Try again.")
            continue
        if seat in storage_seats:
            print("Cannot book storage area (S). Try again.")
            continue
        if seat in taken_seats:
            print("Seat already booked. Try again.")
            continue

        seat_type = get_seat_type(seat)
        price = SEAT_PRICES[seat_type]
        confirm = input(f"Price: ${price} ({seat_type} seat). Confirm? (Y/N): ").upper()
        
        if confirm == "Y":
            taken_seats.add(seat)
            print(f"Booked {seat} for ${price}!")
            break
        else:
            print("Booking cancelled.")
            break

#Function that allows the user to free their seat, effectively canceling their booking
def free_seat():
    while True:  # Loop until valid seat freed
        seat = input("\nEnter seat to free (e.g., 1A): ").upper()
        if seat not in taken_seats:
            print("Seat not booked or invalid. Try again.")
            continue
        taken_seats.remove(seat)
        print(f"Freed {seat}!")
        break
    
# Function that prints the seating plan of the plane.
def show_booking_status():
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
        
#Function that displays the menu which will be shown after every iteration of the program.
def menu():
    print("\n| Apache Airlines Booking System |")
    print("1. Check availability of seat")
    print("2. Book a seat")
    print("3. Free a seat")
    print("4. Show booking status")
    print("5. Exit program")
    
# Main loop
while True:
    menu()
    choice = input("Select an option (1-5): ")
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
        break
    else:
        print("Invalid choice. Try again.")
