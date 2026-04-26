# Hotel Management System Coursework

## 1. Introduction

This is a hotel management application used to create, store reservations, protect against overlapping reservations. The abstract hotel used in this project has classes for hotel rooms, visitors, staff workers and other. To run this program, you need to go to this link: https://github.com/Arturas-Dg/hotel-management-system.git and either clone the repository onto a local device, or download the zip file from Github. Then, you should go the src folder, open main.py file and press run python file. If successful, the terminal will pop up and you should see messages of reserved rooms by imaginary guests and workers. 

## 2. Body / Analysis

There were several requirements for this assignment:
1. Implement the 4 pillars of OOP: 
- Inheritance
- Encapsulation
- Abstraction
- Polymorphism
2. Implement a design pattern
3. Implement composition and aggregation
4. Implement reading and writing to a file

This program fully satisfies the requirements, and further down below each of them it is explained how it was done so.

1. Implementation of 4 pillars of OOP.

# Inheritance

Inheritance has been achieved by creating a parent class Room, and then creating child classes Suite, Penthouse and Standard, which inherit from the Room class. The same principle is used with the parent class User, from which two child classes Guest and Staff are derived, use its methods and attributes. 
![alt text](image.png)

# Encapsulation

Encapsulation, which means hiding objects private data, is implemented by using private variables and methods, which are not accessible from outside the class. For example, the Room class has a private variable _price, which is not accessible from outside the class. Only manager can access it. 
![alt text](image-1.png)

# Abstraction

Abstraction means hiding objects private data, and showing only the necessary information to the user. In this code it is implemented in abstract class User, it cannot be instantiated directly and forces all subclasses to implement the get_role() method.
![alt text](image-2.png)

# Polymorphism

Polymorphism means the same method can produce different behaviour depending on the object it is called on. This program uses subtype polymorphism, where subclasses override methods inherited from a parent class. This is used across Room/Suite/Penthouse classes with set_price and get_price methods. 
![alt text](image-3.png)
![alt text](image-4.png)
![alt text](image-5.png)