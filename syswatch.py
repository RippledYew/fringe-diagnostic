#!/usr/bin/env python3
import psutil
import os
import time
from datetime import datetime
import subprocess


def get_operator():
    name = input("operator name: ")
    return name

operator = get_operator()
subprocess.run('figlet SYSWATCH | lolcat', shell=True)
while True:
    os.system('clear')
    print('===SYSWATCH - Operator: ' + operator + ' ===')
    
    cpu = psutil.cpu_percent(interval=2)
    print("CPU Usage: " + str(cpu) +'%')
    
    ram = psutil.virtual_memory()
    ram_used = round(ram.used / (1024**3), 1)
    ram_total = round(ram.total / (1024**3), 1)
    ram_percent = ram.percent
    print("RAM: " + str(ram_used) + "GB / " + str(ram_total) + "GB (" +str(ram_percent) + "%)")
    
    now = datetime.now().strftime("%H:%M:%S")
    print("Last Update: " + now)
    
    time.sleep(1)