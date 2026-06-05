#1/usr/bin/env python3

from fringe_node import FringeNode

cluster = {
    "Acer": FringeNode("Acer", "online", "10.58.163.167", "learn", "ubuntu 22.04", "intel i5-7200U", 4, 16),
    "Frank": FringeNode("Frank", "pending", "TBD", "compute", "ubuntu 22.04", "dual xeon e5 2699 v4", 44, 256),
    "Egor": FringeNode("Egor", "pending", "TBD", "watchdog", "armbian", "RK3588S", 8, 16),
}

if __name__ == "__main__":
    for name, info in cluster.items():
        print(f"{name} | {info.role} | {info.ip} | {info.status}")
        