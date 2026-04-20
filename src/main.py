# The Base Class (Abstraction & Inheritance)
class Room:
    def __init__(self, room_id, capacity, price_per_night):
        self.room_id = room_id
        self.capacity = capacity
        self._price = price_per_night  
        self.bookings = [] 


class SuiteRoom(Room):
    pass

class StandardRoom(Room):
    pass

class Guest:
    def __init__(self, name, group_size, budget, stay_duration):
        self.name = name
        self.group_size = group_size
        self.budget = budget
        self.stay_duration = stay_duration

class Hotel:
    def __init__(self, name):
        self.name = name
        self.rooms = []        
        self.reservations = [] 