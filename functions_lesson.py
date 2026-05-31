#!/usr/bin/env python3

def greet(name):
    return "Hello " + name + ", welcome to the Fringe."

def main():
    user = input("Enter your name: ")
    message = greet(user)
    print(message)

main()
