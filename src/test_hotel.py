import unittest
import os
from main import Hotel, Room, Suite, Penthouse, Guest, Staff


# Testuojamas Factory patternas - ar teisingai kuriami kambariai
class TestFactory(unittest.TestCase):

    def test_create_standard_room(self):
        # Patikrina ar sukurtas objektas yra Room tipo
        room = Room.create("Standard", "101", 2, 100)
        self.assertIsInstance(room, Room)

    def test_create_suite(self):
        # Patikrina ar sukurtas objektas yra Suite tipo
        suite = Room.create("Suite", "201", 4, 300)
        self.assertIsInstance(suite, Suite)

    def test_create_penthouse(self):
        # Patikrina ar sukurtas objektas yra Penthouse tipo
        penthouse = Room.create("Penthouse", "301", 6, 1000)
        self.assertIsInstance(penthouse, Penthouse)

    def test_create_unknown_type_raises_error(self):
        # Patikrina ar nezinomas tipas meta ValueError klaida
        with self.assertRaises(ValueError):
            Room.create("Cabin", "401", 2, 50)


# Testuojamos rezervacijos - sukurimas, persidengimas, kainos
class TestReservations(unittest.TestCase):

    def setUp(self):
        # Sukuriama svari aplinka pries kiekviena testa
        self.hotel = Hotel("Test Hotel")
        self.room = Room.create("Standard", "101", 2, 100)
        self.hotel.rooms.append(self.room)
        self.guest = Guest("G1", "John Doe", 1, stay_duration=3)

    def test_successful_reservation(self):
        # Patikrina ar rezervacija sekmingai pridedama
        self.guest.reserve_room(self.hotel, self.room, "2026-06-01")
        self.assertEqual(len(self.hotel.reservations), 1)

    def test_overlapping_reservation_is_blocked(self):
        # Patikrina ar persidenganti rezervacija blokuojama
        self.guest.reserve_room(self.hotel, self.room, "2026-06-01")
        guest2 = Guest("G2", "Jane Doe", 1, stay_duration=2)
        guest2.reserve_room(self.hotel, self.room, "2026-06-02")
        self.assertEqual(len(self.hotel.reservations), 1)

    def test_non_overlapping_reservation_succeeds(self):
        # Patikrina ar nesipersidenganti rezervacija leidziama
        self.guest.reserve_room(self.hotel, self.room, "2026-06-01")
        guest2 = Guest("G2", "Jane Doe", 1, stay_duration=2)
        guest2.reserve_room(self.hotel, self.room, "2026-06-10")
        self.assertEqual(len(self.hotel.reservations), 2)

    def test_reservation_total_price(self):
        # Patikrina ar bendra kaina teisingai apskaiciuojama (100/naktis * 3 naktys)
        self.guest.reserve_room(self.hotel, self.room, "2026-06-01")
        total = self.hotel.reservations[0]["total_price"]
        self.assertEqual(total, 300)

    def test_reservation_beyond_limit_date_blocked(self):
        # Patikrina ar rezervacija blokuojama jei virsija limito data
        room_limited = Room.create("Standard", "102", 2, 100, "2026-06-05")
        self.hotel.rooms.append(room_limited)
        guest = Guest("G3", "Bob Smith", 1, stay_duration=10)
        guest.reserve_room(self.hotel, room_limited, "2026-06-01")
        self.assertEqual(len(self.hotel.reservations), 0)

    def test_invalid_date_format_blocked(self):
        # Patikrina ar neteisingas datos formatas blokuojamas
        self.guest.reserve_room(self.hotel, self.room, "01-06-2026")
        self.assertEqual(len(self.hotel.reservations), 0)


# Testuojamas isiregistravimas ir issiregistravimas
class TestCheckInOut(unittest.TestCase):

    def setUp(self):
        # Sukuriama svari aplinka pries kiekviena testa
        self.hotel = Hotel("Test Hotel")
        self.room = Room.create("Standard", "101", 2, 100)
        self.hotel.rooms.append(self.room)
        self.guest = Guest("G1", "John Doe", 1, stay_duration=3)

    def test_check_in_success(self):
        # Patikrina ar svecias sekmingai isiregistruoja
        self.guest.check_in(self.room)
        self.assertIn(self.guest, self.room.occupants)

    def test_check_in_over_capacity_blocked(self):
        # Patikrina ar per didele grupe blokuojama
        big_group = Guest("G2", "Big Group", 5, stay_duration=1)
        big_group.check_in(self.room)
        self.assertNotIn(big_group, self.room.occupants)

    def test_check_out_success(self):
        # Patikrina ar svecias sekmingai issiregistruoja
        self.guest.check_in(self.room)
        self.guest.check_out(self.room)
        self.assertNotIn(self.guest, self.room.occupants)

    def test_check_out_guest_not_in_room(self):
        # Patikrina ar issiregistravimas blokuojamas jei svecio nera kambaryje
        guest2 = Guest("G2", "Jane Doe", 1, stay_duration=1)
        guest2.check_out(self.room)
        self.assertNotIn(guest2, self.room.occupants)


# Testuojama kainos prieiga - tik menedzeris gali matyti ir keisti kainas
class TestPriceAccess(unittest.TestCase):

    def setUp(self):
        # Sukuriamas kambarys, menedzeris ir paprastas darbuotojas
        self.room = Room.create("Standard", "101", 2, 100)
        self.manager = Staff("mgr", "pass", "E001", "Manager")
        self.worker = Staff("wrk", "pass", "E002", "Worker")

    def test_manager_can_get_price(self):
        # Patikrina ar menedzeris gali gauti kaina
        price = self.room.get_price(self.manager)
        self.assertEqual(price, 100)

    def test_worker_cannot_get_price(self):
        # Patikrina ar paprastas darbuotojas negali gauti kainos
        price = self.room.get_price(self.worker)
        self.assertIsNone(price)

    def test_manager_can_set_price(self):
        # Patikrina ar menedzeris gali keisti kaina
        self.room.set_price(self.manager, 200)
        self.assertEqual(self.room._price, 200)

    def test_worker_cannot_set_price(self):
        # Patikrina ar paprastas darbuotojas negali keisti kainos
        self.room.set_price(self.worker, 200)
        self.assertEqual(self.room._price, 100)

    def test_suite_price_multiplier(self):
        # Patikrina ar Suite kaina padauginama is 1.5
        suite = Room.create("Suite", "201", 4, 200)
        suite.set_price(self.manager, 200)
        self.assertEqual(suite._price, 300)

    def test_penthouse_price_multiplier(self):
        # Patikrina ar Penthouse kaina padauginama is 2
        penthouse = Room.create("Penthouse", "301", 6, 500)
        penthouse.set_price(self.manager, 500)
        self.assertEqual(penthouse._price, 1000)


# Testuojamas polimorfizmas - get_role() grazina skirtingas reiksmes
class TestRoles(unittest.TestCase):

    def test_guest_role(self):
        # Patikrina ar svecio role grazinama teisingai
        guest = Guest("G1", "John Doe", 1)
        self.assertEqual(guest.get_role(), "Guest")

    def test_staff_role(self):
        # Patikrina ar darbuotojo role grazinama teisingai
        staff = Staff("mgr", "pass", "E001", "Manager")
        self.assertEqual(staff.get_role(), "Staff - Manager")


# Testuojamas CSV issaugojimas ir ikrovimas
class TestCSV(unittest.TestCase):

    def setUp(self):
        # Sukuriama svari aplinka pries kiekviena testa
        self.hotel = Hotel("Test Hotel")
        self.room = Room.create("Standard", "101", 2, 100)
        self.hotel.rooms.append(self.room)
        self.guest = Guest("G1", "John Doe", 1, stay_duration=3)
        self.filename = "test_reservations.csv"

    def tearDown(self):
        # Isvalomas CSV failas po kiekvieno testo
        if os.path.exists(self.filename):
            os.remove(self.filename)

    def test_save_and_load_reservations(self):
        # Patikrina ar rezervacijos teisingai issaugomos ir ikraunamos
        self.guest.reserve_room(self.hotel, self.room, "2026-06-01")
        self.hotel.save_reservations_to_csv(self.filename)
        self.hotel.reservations.clear()
        self.hotel.load_reservations_from_csv(self.filename)
        self.assertEqual(len(self.hotel.reservations), 1)

    def test_load_nonexistent_file(self):
        # Patikrina ar programa nesuluza jei failo nera
        self.hotel.load_reservations_from_csv("nonexistent.csv")
        self.assertEqual(len(self.hotel.reservations), 0)


if __name__ == "__main__":
    unittest.main()