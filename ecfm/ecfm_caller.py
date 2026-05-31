#! /usr/bin/env python3
import subprocess
import time

subprocess.run('figlet FRINGE | lolcat', shell=True)

while True:
    subprocess.run('clear', shell=True)
    print("=== Ecfm Caller ===")
    print("1. Run smoke test")
    print("2. View reports")
    print("3. Check ECFM folder")
    print("4. Exit")

    choice = input("Select: ")
    
    if choice == "1":
        subprocess.run(['python3', '/home/ripple/python/ecfm/ecfm_runner.py'])
    elif choice == "2":
        subprocess.run(['ls', '/home/ripple/python/ecfm/'])
    elif choice == "3":
        subprocess.run(['ls', '-lh', '/home/ripple/python/ecfm/'])    
    elif choice == "4":
        print("Bye")
        break
    else:
        print("Invalid choice")
    time.sleep(2)
    