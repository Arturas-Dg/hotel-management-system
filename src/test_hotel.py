import unittest
from main import Hotel, Room, Guest, Staff

class TestReservations(unittest.TestCase):
    
    def setUp(self):
        self.hotel = Hotel("Test Hotel")
        self.room = Room.create("Standard", "101", 2, 100)
        self.hotel.rooms.append(self.room)
        self.guest = Guest("G1", "John Doe", 1, stay_duration=3)

    def test_successful_reservation(self):
        self.guest.reserve_room(self.hotel, self.room, "2026-06-01")
        self.assertEqual(len(self.hotel.reservations), 1) 

    def test_overlapping_reservation(self):
        self.guest.reserve_room(self.hotel, self.room, "2026-06-01")
        guest2 = Guest("G2", "Jane Doe", 1, stay_duration=2)
        guest2.reserve_room(self.hotel, self.room, "2026-06-02") 
        self.assertEqual(len(self.hotel.reservations), 1) 

if __name__ == "__main__":
    unittest.main()