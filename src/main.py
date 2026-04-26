import csv
import os
from datetime import datetime, timedelta
from abc import ABC, abstractmethod


class Hotel:
    def __init__(self, name):
        self.name = name
        self.rooms = []
        self.reservations = []

    def save_reservations_to_csv(self, filename="reservations.csv"):
        with open(filename, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Room ID", "Guest ID", "Start Date", "End Date", "Total Price"])
            for res in self.reservations:
                start_str = res["start_date"].strftime("%Y-%m-%d")
                end_str = res["end_date"].strftime("%Y-%m-%d")
                writer.writerow([res["room"].room_id, res["guest"].guest_id, start_str, end_str, res.get("total_price", 0)])
        print(f"Successfully saved to {filename}")

    def load_reservations_from_csv(self, filename="reservations.csv"):
        if not os.path.exists(filename):
            print(f"No previous reservation file found at {filename}")
            return
            
        with open(filename, mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                room_id = row["Room ID"]
                guest_id = row["Guest ID"]
                start_str = row["Start Date"]
                end_str = row["End Date"]
                total_price = float(row.get("Total Price", 0))
                
                room_obj = next((r for r in self.rooms if r.room_id == room_id), None)
                if not room_obj:
                    continue
                    
                dummy_guest = Guest(guest_id, f"Guest_{guest_id}", 1)
                start_date = datetime.strptime(start_str, "%Y-%m-%d")
                end_date = datetime.strptime(end_str, "%Y-%m-%d")
                
                self.reservations.append({
                    "guest": dummy_guest,
                    "room": room_obj,
                    "start_date": start_date,
                    "end_date": end_date,
                    "total_price": total_price
                })
        print(f"Reservations successfully loaded from {filename}")

    def cancel_reservation(self, guest_id, room_id):
        for res in self.reservations:
            if res["guest"].guest_id == guest_id and res["room"].room_id == room_id:
                self.reservations.remove(res)
                print(f"Reservation for guest {guest_id} in room {room_id} has been cancelled.")
                return
        print(f"No reservation found for guest {guest_id} in room {room_id}.")   

            

    def display_rooms(self):
        print(f"\n--- {self.name} Room Status ---")
        for room in self.rooms:
            status = "Occupied" if room.guest_count > 0 else "Free"
            print(f"Room {room.room_id} (Capacity: {room.capacity}): {status} - Guests: {room.guest_count}")
        print("---------------------------\n")

class Room:
    @staticmethod
    def create(room_type, room_id, capacity, price_per_night, reservation_limit_date=None):
        if room_type == "Suite":
            return Suite(room_id, capacity, price_per_night, reservation_limit_date)
        elif room_type == "Penthouse":
            return Penthouse(room_id, capacity, price_per_night, reservation_limit_date)
        elif room_type == "Standard":
            return Room(room_id, capacity, price_per_night, reservation_limit_date)
        else:
            raise ValueError(f"Unknown room type: {room_type}")

    def __init__(self, room_id, capacity, price_per_night, reservation_limit_date=None):
        self.room_id = room_id
        self.capacity = capacity
        self._price = price_per_night  
        self.reservation_limit_date = reservation_limit_date
        self.bookings = [] 
        self.occupants = []

    @property
    def guest_count(self):
        return sum(guest.group_size for guest in self.occupants)

    def set_price(self, user, new_price):
        if isinstance(user, Staff) and user.role == "Manager":
            self._price = new_price
        else:
            print("Access Denied: Only a Manager can change the room price.")

    def get_price(self, user):
        if isinstance(user, Staff) and user.role == "Manager":
            return self._price
        else:
            print("Access Denied: Only a Manager can view the exact room price directly.")
            return None

class Suite(Room):
    def __init__(self, room_id, capacity, price_per_night, reservation_limit_date=None):
        super().__init__(room_id, capacity, price_per_night, reservation_limit_date)

    def set_price(self, user, new_price):
        if isinstance(user, Staff) and user.role == "Manager":
            self._price = new_price * 1.5
        else:
            print("Access Denied: Only a Manager can change the room price.")

    def get_price(self, user):
        if isinstance(user, Staff) and user.role == "Manager":
            return self._price
        else:
            print("Access Denied: Only a Manager can view the exact room price directly.")
            return None

class Penthouse(Room):
    def __init__(self, room_id, capacity, price_per_night, reservation_limit_date=None):
        super().__init__(room_id, capacity, price_per_night, reservation_limit_date)

    def set_price(self, user, new_price):
        if isinstance(user, Staff) and user.role == "Manager":
            self._price = new_price * 2
        else:
            print("Access Denied: Only a Manager can change the room price.")

    def get_price(self, user):
        if isinstance(user, Staff) and user.role == "Manager":
            return self._price
        else:
            print("Access Denied: Only a Manager can view the exact room price directly.")
            return None



class User(ABC):
    @abstractmethod
    def get_role(self):
        pass

class Guest(User):
    def __init__(self, guest_id, full_name, group_size, stay_duration=1):
        self.guest_id = guest_id
        self.full_name = full_name
        self.group_size = group_size 
        self.stay_duration = stay_duration

    def get_role(self):
        return "Guest"

    def reserve_room(self, hotel, room, start_date_str):
        try:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
        except ValueError:
            print("Invalid date format. Please use YYYY-MM-DD.")
            return

        end_date = start_date + timedelta(days=self.stay_duration)

        if room.reservation_limit_date:
            limit_date = datetime.strptime(room.reservation_limit_date, "%Y-%m-%d")
            if end_date > limit_date:
                print(f"Cannot reserve room {room.room_id}. It is only available until {room.reservation_limit_date}.")
                return
            
        for res in hotel.reservations:
            if res["room"].room_id == room.room_id:
                if start_date < res["end_date"] and res["start_date"] < end_date:
                    print(f"Room {room.room_id} is already taken from {res['start_date'].strftime('%Y-%m-%d')} to {res['end_date'].strftime('%Y-%m-%d')}.")
                    return
            
            
        total_price = room._price * self.stay_duration
        hotel.reservations.append({
            "guest": self, 
            "room": room, 
            "start_date": start_date, 
            "end_date": end_date,
            "total_price": total_price
        })
        print(f"Guest {self.full_name} reserved room {room.room_id} from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}. Total price: ${total_price}")

    def check_in(self, room):
        if room.guest_count + self.group_size <= room.capacity:
            room.occupants.append(self)
            print(f"Guest {self.full_name} checking into room {room.room_id} for {self.stay_duration} nights.")
        else:
            print(f"Room {room.room_id} does not have enough capacity for a group of {self.group_size}.")

    def check_out(self, room):
        if self in room.occupants:
            room.occupants.remove(self)
            print(f"Guest {self.full_name} checking out. Room {room.room_id} is now free.")
        else:
            print(f"Guest {self.full_name} is not in room {room.room_id}.")

class Staff(User):
    def __init__(self, username, password, employee_id, role="Worker"):
        self.username = username
        self.password = password
        self.employee_id = employee_id
        self.role = role

    def get_role(self):
        return f"Staff - {self.role}"

    def get_reservation_price(self, hotel, room_id, guest_id):
        """Allows Staff to retrieve the total price of a guest's reservation."""
        for res in hotel.reservations:
            if res["room"].room_id == room_id and res["guest"].guest_id == guest_id:
                return res.get("total_price", 0)
        print("Reservation not found.")
        return None

if __name__ == "__main__":
    hotel = Hotel("Grand Hotel")
    
    room1 = Room.create("Standard", "101", 2, 100, "2026-12-31")
    suite1 = Room.create("Suite", "201", 4, 300)
    penthouse1 = Room.create("Penthouse", "301", 6, 1000)
    
    hotel.rooms.append(room1)
    hotel.rooms.append(suite1)
    hotel.rooms.append(penthouse1)

    guest1 = Guest("G1", "John Doe", 1, stay_duration=3)
    guest2 = Guest("G2", "Jane Doe", 2, stay_duration=2)
    guest3 = Guest("G3", "Bob Smith", 1, stay_duration=5)
    guest4 = Guest("G4", "Alice Brown", 3, stay_duration=1)
    guest5 = Guest("G5", "Carlos Rivera", 4, stay_duration=7)

    print("\n--- Making reservations ---")
    guest1.reserve_room(hotel, room1, "2026-05-01")
    guest2.reserve_room(hotel, suite1, "2026-05-01")
    guest3.reserve_room(hotel, room1, "2026-05-10")   # after guest1 checks out
    guest4.reserve_room(hotel, penthouse1, "2026-05-03")
    guest5.reserve_room(hotel, penthouse1, "2026-05-01")  # blocked, over capacity

    print("\n--- Attempting overlapping reservation ---")
    guest2.reserve_room(hotel, room1, "2026-05-02")  # blocked, overlaps guest1

    print("\n--- Saving to CSV ---")
    hotel.save_reservations_to_csv("reservations.csv")

    hotel.reservations.clear()

    print("\n--- Loading from CSV ---")
    hotel.load_reservations_from_csv("reservations.csv")
    print(f"Loaded {len(hotel.reservations)} reservations from CSV.")
    for res in hotel.reservations:
        print(f"Loaded reservation: Guest {res['guest'].guest_id} in Room {res['room'].room_id} from {res['start_date'].strftime('%Y-%m-%d')} to {res['end_date'].strftime('%Y-%m-%d')} (Price: ${res.get('total_price', 0)})")

    print("\n--- Staff verifying price ---")
    staff_member = Staff("Arturas", "pass789", "E001", "Manager")
    price = staff_member.get_reservation_price(hotel, "101", "G1")
    print(f"Staff member {staff_member.username} retrieved reservation price: ${price}")