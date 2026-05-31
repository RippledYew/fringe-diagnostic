#!/usr/bin/env python3
import os
import psutil
import subprocess
from datetime import datetime

def get_operator():
    name = input("Operator Name: ")
    return name

operator = get_operator()
subprocess.run('figlet FRINGE | lolcat', shell=True)


name = "Ripple"
node = "Acer"
status = "online"

print("=== REPORTER - Operator: " + operator + " ===")
print(name + " reporting from " + node + " _status: " + status)

cpu_count = os.cpu_count()
print("CPU Cores: " + str(cpu_count))

ram = psutil.virtual_memory()
ram_total = round(ram.total / (1024**3), 1)
ram_used = round(ram.used / (1024**3), 1)
print("RAM total: " + str(ram_total) + "GB")
print("RAM used: " + str(ram_used) + "GB")

partitions = psutil.disk_partitions()
for partition in partitions:
    if '/snap' in partition.mountpoint:
        continue
    usage = psutil.disk_usage(partition.mountpoint)
    total = round(usage.total / (1024**3), 1)
    used = round(usage.used / (1024**3), 1)
    print("Partition: " + partition.mountpoint + " | Total: " + str(total) + "GB | Used: " + str(used) + "GB")
    
result = subprocess.run(['hostname', '-I'], capture_output=True, text=True)
ip = result.stdout.strip().split()[0]
print("Hostname; " + node)
print("IP: " + ip)