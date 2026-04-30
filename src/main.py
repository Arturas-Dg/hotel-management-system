import csv
import os
from datetime import datetime, timedelta
from abc import ABC, abstractmethod


# Jei viešbutis ištrinamas, kambariai taip pat išnyksta
class Hotel:
    def __init__(self, name):
        self.name = name
        self.rooms = []  # Kompozicija, viešbutis valdo kambarius

        # Agregacija, rezervacijos susieja svečius ir kambarius
        # Svečias ir kambarys egzistuoja nepriklausomai, tik rezervacija juos susieja
        self.reservations = []

    def save_reservations_to_csv(self, filename="reservations.csv"):
    # Atidaro CSV faila rasymui, jei failo nera - sukuria nauja
        with open(filename, mode='w', newline='') as file:
            writer = csv.writer(file)
            # Irasomi stulpeliu pavadinimai
            writer.writerow(["Room ID", "Guest ID", "Start Date", "End Date", "Total Price"])
            for res in self.reservations:   
                # Datos paverciamos i teksta, nes CSV negali saugoti datetime objektu
                start_str = res["start_date"].strftime("%Y-%m-%d")
                end_str = res["end_date"].strftime("%Y-%m-%d")
                # Kiekviena rezervacija irasoma kaip atskira eilute
                writer.writerow([res["room"].room_id, res["guest"].guest_id, start_str, end_str, res.get("total_price", 0)])
        print(f"Successfully saved to {filename}")

    def load_reservations_from_csv(self, filename="reservations.csv"):
        # Patikrina ar failas egzistuoja, jei ne - baigia funkcija
        if not os.path.exists(filename):
            print(f"No previous reservation file found at {filename}")
            return
            
        # Atidaro faila skaitymui
        with open(filename, mode='r') as file:
            # DictReader leidzia pasiekti stulpelius pagal pavadinima, o ne indeksa
            reader = csv.DictReader(file)
            for row in reader:
                # Nuskaitomos reiksmes is kiekvienos eilutes
                room_id = row["Room ID"]
                guest_id = row["Guest ID"]
                start_str = row["Start Date"]
                end_str = row["End Date"]
                total_price = float(row.get("Total Price", 0))
                
                # Iesko kambario objekto pagal ID, jei nerandama - praleidzia eilute
                room_obj = next((r for r in self.rooms if r.room_id == room_id), None)
                if not room_obj:
                    continue    

                # Sukuriamas laikinas svecio objektas su duomenimis is CSV
                dummy_guest = Guest(guest_id, f"Guest_{guest_id}", 1)
                # Datos paverciamos atgal i datetime objektus
                start_date = datetime.strptime(start_str, "%Y-%m-%d")
                end_date = datetime.strptime(end_str, "%Y-%m-%d")
                
                # Rezervacija pridedama atgal i sarasa
                self.reservations.append({
                    "guest": dummy_guest,
                    "room": room_obj,
                    "start_date": start_date,
                    "end_date": end_date,
                    "total_price": total_price
                })
        print(f"Reservations successfully loaded from {filename}")

#iskvietus metoda eina per rezervaciju sarasa, jei randa atitikmeni, istrina is saraso
    def cancel_reservation(self, guest_id, room_id):
        # Eina per visas rezervacijas ieskodamas atitinkamo svecio ir kambario
        for res in self.reservations:
            if res["guest"].guest_id == guest_id and res["room"].room_id == room_id:
                # Jei randama - istrina rezervacija is saraso ir baigia funkcija
                self.reservations.remove(res)
                print(f"Reservation for guest {guest_id} in room {room_id} has been cancelled.")
                return
        # Jei rezervacija nerasta - pranese apie tai
        print(f"No reservation found for guest {guest_id} in room {room_id}.")



    def display_rooms(self):
        print(f"\n--- {self.name} Room Status ---")
        for room in self.rooms:
            status = "Occupied" if room.guest_count > 0 else "Free"
            print(f"Room {room.room_id} (Capacity: {room.capacity}): {status} - Guests: {room.guest_count}")
        print("---------------------------\n")

#Sita klasė yra ir bazinė klasė, ir standartinio kambario klasė, todėl reikia ją palikti ne abstrakcia, kitaip reiktu kurti papildoma StandardRoom klasę

class Room:
    @staticmethod

    # Čia naudojamas Factory pattern iš dzaino patternų. Kadangi tai yra tik konceptas, neprivaloma kurti papildomų klasių norint jį įgyvendinti.
    # Toks patternas naudojamas, nes yra keli kambarių tipai, kurie visi turi didelę dalį vienodo funkcionalumo, tačiau kai kuriose vietose skiriasi.
    #singleton netinka, nes reikia daug kambarių tipų, o ne vieno.
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
        self._price = price_per_night  # Privatus kintamasis - tiesiogiai nepasiekiamas is isores
        self.reservation_limit_date = reservation_limit_date  # Data iki kurios galima rezervuoti
        self.bookings = []
        self.occupants = []  # Dabar kambaryje esantys sveciai

    # @property leidzia pasiekti metoda kaip atributa, be skliaustų (room.guest_count, o ne room.guest_count())
    @property
    def guest_count(self):
        return sum(guest.group_size for guest in self.occupants)

    # kaina gali keisti tik Menedzeris
    def set_price(self, user, new_price):
        if isinstance(user, Staff) and user.role == "Manager":
            self._price = new_price
        else:
            print("Access Denied: Only a Manager can change the room price.")

    #  kaina gali matyti tik Menedzeris
    def get_price(self, user):
        if isinstance(user, Staff) and user.role == "Manager":
            return self._price
        else:
            print("Access Denied: Only a Manager can view the exact room price directly.")
            return None
# Suite paveldi is Room klases - gauna visus Room atributus ir metodus
class Suite(Room):
    def __init__(self, room_id, capacity, price_per_night, reservation_limit_date=None):
        # super() iskviecia Room __init__ - nereikia perrasinet to paties kodo
        super().__init__(room_id, capacity, price_per_night, reservation_limit_date)

    # Metodo perrasymas (method overriding)s
    # Suite kaina padauginama is 1.5, skirtingai nei paprastame kambaryje
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

# Penthouse paveldi is Room klases - tas pats principas kaip Suite
class Penthouse(Room):
    def __init__(self, room_id, capacity, price_per_night, reservation_limit_date=None):
        super().__init__(room_id, capacity, price_per_night, reservation_limit_date)

    # Metodo perrasymas (method overriding) - polimorfizmas
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

# Abstrakti klase - negali buti sukurta tiesiogiai, tik per poklases
# Vercia visas poklases implementuoti get_role() metoda
class User(ABC):
    @abstractmethod
    def get_role(self):
        pass

# Guest paveldi is User - privalo implementuoti get_role()
class Guest(User):
    def __init__(self, guest_id, full_name, group_size, stay_duration=1):
        self.guest_id = guest_id
        self.full_name = full_name
        self.group_size = group_size
        self.stay_duration = stay_duration

    # get_role() grazina skirtinga reiksme nei Staff klaseje
    def get_role(self):
        return "Guest"

    def reserve_room(self, hotel, room, start_date_str):
        try:
            # Datos formato patikrinimas - jei neteisingas, baigia funkcija
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
        except ValueError:
            print("Invalid date format. Please use YYYY-MM-DD.")
            return

        end_date = start_date + timedelta(days=self.stay_duration)

        # Patikrina ar rezervacija nevirsija kambario rezervavimo limito
        if room.reservation_limit_date:
            limit_date = datetime.strptime(room.reservation_limit_date, "%Y-%m-%d")
            if end_date > limit_date:
                print(f"Cannot reserve room {room.room_id}. It is only available until {room.reservation_limit_date}.")
                return

        # Patikrina ar datos nesikerta su jau esamomis rezervacijomis
        for res in hotel.reservations:
            if res["room"].room_id == room.room_id:
                if start_date < res["end_date"] and res["start_date"] < end_date:
                    print(f"Room {room.room_id} is already taken from "
                          f"{res['start_date'].strftime('%Y-%m-%d')} to "
                          f"{res['end_date'].strftime('%Y-%m-%d')}.")
                    return

        # Apskaiciuoja bendra kaina ir prideda rezervacija i sarasa
        total_price = room._price * self.stay_duration
        hotel.reservations.append({
            "guest": self,
            "room": room,
            "start_date": start_date,
            "end_date": end_date,
            "total_price": total_price
        })
        print(f"Guest {self.full_name} reserved room {room.room_id} "
              f"from {start_date.strftime('%Y-%m-%d')} to "
              f"{end_date.strftime('%Y-%m-%d')}. Total price: ${total_price}")

    def check_in(self, room):
        # Patikrina ar kambaryje uztenka vietos grupei
        if room.guest_count + self.group_size <= room.capacity:
            room.occupants.append(self)
            print(f"Guest {self.full_name} checking into room {room.room_id} "
                  f"for {self.stay_duration} nights.")
        else:
            print(f"Room {room.room_id} does not have enough capacity "
                  f"for a group of {self.group_size}.")

    def check_out(self, room):
            # Patikrina ar svecias is tikro yra kambaryje
            if self in room.occupants:
                room.occupants.remove(self)
                print(f"Guest {self.full_name} checking out. Room {room.room_id} is now free.")
            else:
                # Jei svecio nera kambaryje - pranese apie tai
                print(f"Guest {self.full_name} is not in room {room.room_id}.")

    # Staff paveldi is User - privalo implementuoti get_role()
class Staff(User):
    def __init__(self, username, password, employee_id, role="Worker"):
        self.username = username
        self.password = password  # Inkapsuliacija - slaptazodis saugomas objekte
        self.employee_id = employee_id
        self.role = role  # Numatyta reiksme "Worker" jei role nenurodyta

    # Polimorfizmas - get_role() grazina skirtinga reiksme nei Guest klaseje
    def get_role(self):
        return f"Staff - {self.role}"

    def get_reservation_price(self, hotel, room_id, guest_id):
        """Allows Staff to retrieve the total price of a guest's reservation."""
        # Eina per rezervacijas ieskodamas atitinkamo kambario ir svecio
        for res in hotel.reservations:
            if res["room"].room_id == room_id and res["guest"].guest_id == guest_id:
                # Jei randama - grazina bendra kaina
                return res.get("total_price", 0)
        # Jei rezervacija nerasta - pranese apie tai
        print("Reservation not found.")
        return None
if __name__ == "__main__":
    # Sukuriamas viešbutis
    hotel = Hotel("Grand Hotel")
    
    # Kambariai kuriami per Factory methoda - nereikia tiesiogiai kviesti Suite() ar Penthouse()
    room1 = Room.create("Standard", "101", 2, 100, "2026-12-31")
    suite1 = Room.create("Suite", "201", 4, 300)
    penthouse1 = Room.create("Penthouse", "301", 6, 1000)
    
    # Kambariai pridedami i viešbuti - kompozicija
    hotel.rooms.append(room1)
    hotel.rooms.append(suite1)
    hotel.rooms.append(penthouse1)

    # Sveciai sukuriami su skirtingais duomenimis
    guest1 = Guest("G1", "John Doe", 1, stay_duration=3)
    guest2 = Guest("G2", "Jane Doe", 2, stay_duration=2)
    guest3 = Guest("G3", "Bob Smith", 1, stay_duration=5)
    guest4 = Guest("G4", "Alice Brown", 3, stay_duration=1)
    guest5 = Guest("G5", "Carlos Rivera", 4, stay_duration=7)

    print("\n--- Making reservations ---")
    guest1.reserve_room(hotel, room1, "2026-05-01")
    guest2.reserve_room(hotel, suite1, "2026-05-01")
    guest3.reserve_room(hotel, room1, "2026-05-10")   # po guest1 isvykimo
    guest4.reserve_room(hotel, penthouse1, "2026-05-03")
    guest5.reserve_room(hotel, penthouse1, "2026-05-01")  # blokuojama - per didele grupe

    print("\n--- Attempting overlapping reservation ---")
    # Blokuojama - datos persidengia su guest1 rezervacija
    guest2.reserve_room(hotel, room1, "2026-05-02")

    print("\n--- Saving to CSV ---")
    # Rezervacijos issaugomos i CSV faila
    hotel.save_reservations_to_csv("reservations.csv")

    # Rezervacijos istrinamos is atminties - simuliuojamas programos paleidimas is naujo
    hotel.reservations.clear()

    print("\n--- Loading from CSV ---")
    # Rezervacijos ikraunamos atgal is CSV failo
    hotel.load_reservations_from_csv("reservations.csv")
    print(f"Loaded {len(hotel.reservations)} reservations from CSV.")
    for res in hotel.reservations:
        guest_id = res['guest'].guest_id
        room_id = res['room'].room_id
        start = res['start_date'].strftime('%Y-%m-%d')
        end = res['end_date'].strftime('%Y-%m-%d')
        price = res.get('total_price', 0)
        print(f"Loaded reservation: Guest {guest_id} in Room {room_id} "
              f"from {start} to {end} (Price: ${price})")

    print("\n--- Staff verifying price ---")
    # Darbuotojas sukuriamas su Manager role
    staff_member = Staff("Arturas", "pass789", "E001", "Manager")
    # Menedzeris gauna rezervacijos kaina
    price = staff_member.get_reservation_price(hotel, "101", "G1")
    print(f"Staff member {staff_member.username} retrieved reservation price: ${price}")

    print("\n--- Cancelling guest1's reservation ---")
    # Rezervacija panaikinama ir issaugoma atnaujinta versija i CSV
    hotel.cancel_reservation("G1", "101")
    hotel.save_reservations_to_csv("reservations.csv")
    hotel.save_reservations_to_csv("reservations.csv")