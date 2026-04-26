import unittest
import os
from main import Hotel, Room, Suite, Penthouse, Guest, Staff


class TestFactory(unittest.TestCase):

    def test_create_standard_room(self):
        room = Room.create("Standard", "101", 2, 100)
        self.assertIsInstance(room, Room)

    def test_create_suite(self):
        suite = Room.create("Suite", "201", 4, 300)
        self.assertIsInstance(suite, Suite)

    def test_create_penthouse(self):
        penthouse = Room.create("Penthouse", "301", 6, 1000)
        self.assertIsInstance(penthouse, Penthouse)

    def test_create_unknown_type_raises_error(self):
        with self.assertRaises(ValueError):
            Room.create("Cabin", "401", 2, 50)
    

class TestReservations(unittest.TestCase):

    def setUp(self):
        self.hotel = Hotel("Test Hotel")
        self.room = Room.create("Standard", "101", 2, 100)
        self.hotel.rooms.append(self.room)
        self.guest = Guest("G1", "John Doe", 1, stay_duration=3)

    def test_successful_reservation(self):
        self.guest.reserve_room(self.hotel, self.room, "2026-06-01")
        self.assertEqual(len(self.hotel.reservations), 1)

    def test_overlapping_reservation_is_blocked(self):
        self.guest.reserve_room(self.hotel, self.room, "2026-06-01")
        guest2 = Guest("G2", "Jane Doe", 1, stay_duration=2)
        guest2.reserve_room(self.hotel, self.room, "2026-06-02")
        self.assertEqual(len(self.hotel.reservations), 1)

    def test_non_overlapping_reservation_succeeds(self):
        self.guest.reserve_room(self.hotel, self.room, "2026-06-01")
        guest2 = Guest("G2", "Jane Doe", 1, stay_duration=2)
        guest2.reserve_room(self.hotel, self.room, "2026-06-10")
        self.assertEqual(len(self.hotel.reservations), 2)

    def test_reservation_total_price(self):
        self.guest.reserve_room(self.hotel, self.room, "2026-06-01")
        total = self.hotel.reservations[0]["total_price"]
        self.assertEqual(total, 300)  # 100/night * 3 nights

    def test_reservation_beyond_limit_date_blocked(self):
        room_limited = Room.create("Standard", "102", 2, 100, "2026-06-05")
        self.hotel.rooms.append(room_limited)
        guest = Guest("G3", "Bob Smith", 1, stay_duration=10)
        guest.reserve_room(self.hotel, room_limited, "2026-06-01")
        self.assertEqual(len(self.hotel.reservations), 0)

    def test_invalid_date_format_blocked(self):
        self.guest.reserve_room(self.hotel, self.room, "01-06-2026")
        self.assertEqual(len(self.hotel.reservations), 0)


class TestCheckInOut(unittest.TestCase):

    def setUp(self):
        self.hotel = Hotel("Test Hotel")
        self.room = Room.create("Standard", "101", 2, 100)
        self.hotel.rooms.append(self.room)
        self.guest = Guest("G1", "John Doe", 1, stay_duration=3)

    def test_check_in_success(self):
        self.guest.check_in(self.room)
        self.assertIn(self.guest, self.room.occupants)

    def test_check_in_over_capacity_blocked(self):
        big_group = Guest("G2", "Big Group", 5, stay_duration=1)
        big_group.check_in(self.room)
        self.assertNotIn(big_group, self.room.occupants)

    def test_check_out_success(self):
        self.guest.check_in(self.room)
        self.guest.check_out(self.room)
        self.assertNotIn(self.guest, self.room.occupants)

    def test_check_out_guest_not_in_room(self):
        guest2 = Guest("G2", "Jane Doe", 1, stay_duration=1)
        guest2.check_out(self.room)
        self.assertNotIn(guest2, self.room.occupants)


class TestPriceAccess(unittest.TestCase):

    def setUp(self):
        self.room = Room.create("Standard", "101", 2, 100)
        self.manager = Staff("mgr", "pass", "E001", "Manager")
        self.worker = Staff("wrk", "pass", "E002", "Worker")

    def test_manager_can_get_price(self):
        price = self.room.get_price(self.manager)
        self.assertEqual(price, 100)

    def test_worker_cannot_get_price(self):
        price = self.room.get_price(self.worker)
        self.assertIsNone(price)

    def test_manager_can_set_price(self):
        self.room.set_price(self.manager, 200)
        self.assertEqual(self.room._price, 200)

    def test_worker_cannot_set_price(self):
        self.room.set_price(self.worker, 200)
        self.assertEqual(self.room._price, 100)  # unchanged

    def test_suite_price_multiplier(self):
        suite = Room.create("Suite", "201", 4, 200)
        suite.set_price(self.manager, 200)
        self.assertEqual(suite._price, 300)  # 200 * 1.5

    def test_penthouse_price_multiplier(self):
        penthouse = Room.create("Penthouse", "301", 6, 500)
        penthouse.set_price(self.manager, 500)
        self.assertEqual(penthouse._price, 1000)  # 500 * 2


class TestRoles(unittest.TestCase):

    def test_guest_role(self):
        guest = Guest("G1", "John Doe", 1)
        self.assertEqual(guest.get_role(), "Guest")

    def test_staff_role(self):
        staff = Staff("mgr", "pass", "E001", "Manager")
        self.assertEqual(staff.get_role(), "Staff - Manager")


class TestCSV(unittest.TestCase):

    def setUp(self):
        self.hotel = Hotel("Test Hotel")
        self.room = Room.create("Standard", "101", 2, 100)
        self.hotel.rooms.append(self.room)
        self.guest = Guest("G1", "John Doe", 1, stay_duration=3)
        self.filename = "test_reservations.csv"

    def tearDown(self):
        if os.path.exists(self.filename):
            os.remove(self.filename)

    def test_save_and_load_reservations(self):
        self.guest.reserve_room(self.hotel, self.room, "2026-06-01")
        self.hotel.save_reservations_to_csv(self.filename)
        self.hotel.reservations.clear()
        self.hotel.load_reservations_from_csv(self.filename)
        self.assertEqual(len(self.hotel.reservations), 1)

    def test_load_nonexistent_file(self):
        self.hotel.load_reservations_from_csv("nonexistent.csv")
        self.assertEqual(len(self.hotel.reservations), 0)


if __name__ == "__main__":
    unittest.main()