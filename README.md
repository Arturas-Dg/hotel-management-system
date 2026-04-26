# Hotel Management System Coursework

## 1. Introduction

This is a hotel management application used to create, store reservations, protect against overlapping reservations. The abstract hotel used in this project has classes for hotel rooms, visitors, staff workers and other. To run this program, you need to go to this link: https://github.com/Arturas-Dg/hotel-management-system.git and either clone the repository onto a local device, or download the zip file from Github. Then, you should go the src folder, open

## 2. Body / Analysis

### Implementation of Functional Requirements

This program satisfies the core functional requirements, including data persistence.

- **Reading/Writing to File:** The program uses the `csv` library to save and load reservations to a `reservations.csv` file, ensuring data is not lost between sessions.
  _(Include a small 3-4 line snippet of your `save_reservations_to_csv` function here)_

### 4 Pillars of Object-Oriented Programming

The program implements all four OOP pillars as follows:

- **1. Inheritance:** \* **What it is:** A mechanism where a new class derives properties and behaviors from an existing class.
  - **How it was used:** The `Guest` and `Staff` classes inherit from the base `User` class.
    _(Insert a small code snippet showing `class Guest(User):`)_

- **2. Encapsulation:**
  - **What it is:** Bundling data and methods that operate on that data within one unit, and restricting direct access to some of the object's components.
  - **How it was used:** The `Room` class encapsulates the `_price` attribute. It cannot be accessed directly; instead, it requires the `get_price()` and `set_price()` methods, which verify if the user is an Admin.
    _(Insert a small code snippet showing the `_price` logic)_

- **3. Abstraction:**
  - **What it is:** Hiding complex implementation details and showing only the essential features of the object.
  - **How it was used:** _(Explain the abstract class/method you add, e.g., the `User` class having an abstract `get_details()` method)_.

- **4. Polymorphism:**
  - **What it is:** The ability of different objects to respond to the same method call in their own specific way.
  - **How it was used:** _(Explain how calling a method like `perform_duty()` on both a Guest and Staff object yields different results)_.

### Design Pattern: Factory Method

- **What it is:** A creational pattern that provides an interface for creating objects in a superclass, but allows subclasses to alter the type of objects that will be created.
- **Why it is suitable:** In scenarios where we need different types of rooms (e.g., Standard vs. Suite) with varying capacities and base prices, the Factory Pattern provides a flexible approach to instantiate them without cluttering the main logic.
- **How it works in code:** _(Insert a snippet of your RoomFactory class)_.

### Composition and Aggregation

- **Aggregation:** The `Hotel` class contains a list of `Room` objects. This is aggregation because if the hotel is "destroyed" in the code, the concept of the rooms still exists independently.
- _(Insert snippet showing `self.rooms = []` inside Hotel)_

---

## 3. Results and Summary

### Results

- The program successfully tracks room availability, handles overlapping booking logic, and accurately writes states to a CSV file.
- Integrating the Factory pattern streamlined object creation but initially caused bugs with attribute assignments.
- A major challenge was handling the `datetime` logic to accurately calculate and prevent overlapping reservations for the same room.
- Implementing unit tests revealed edge cases in the CSV loading logic that were subsequently patched.

### Conclusions

- **What has this work achieved?** This coursework successfully consolidated theoretical OOP knowledge into a functional, multi-class system.
- **What is the result of your work?** A robust CLI application capable of acting as the backend foundation for a hotel booking interface.
- **Future Prospects:** The application could be extended by adding a Graphical User Interface (GUI) using Tkinter, integrating a proper SQL database instead of CSVs, and adding a billing/invoicing module for the `Staff` to use.

---

## 4. Resources

- [Python 3.10 Documentation](https://docs.python.org/3/)
- [Refactoring Guru: Factory Method](https://refactoring.guru/design-patterns/factory-method)
- [PEP 8 Style Guide](https://peps.python.org/pep-0008/)
