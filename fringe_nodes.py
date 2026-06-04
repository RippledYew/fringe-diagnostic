#1/usr/bin/env python3

cluster = {
    "Acer": {
        "ip": "10.58.163.167",
        "role": "learn",
        "os": "ubuntu 22.04",
        "cpu": "intel i5-7200U",
        "cores": 4,
        "ram_gb": 16,
        "status": "online"
    },
    "Frank": {
        "ip": "TBD",
        "role": "compute",
        "os": "Ubuntu 24.04",
        "cpu": "Dual Xeon e5-2699v4",
        "cores": 88,
        "ram_gb": 256,
        "status": "pending"
    },
    "Egor": {
        "ip": "TBD",
        "role": "watchdog",
        "os": "Armbian",
        "cpu": "RK3588S",
        "cores":8,
        "ram_gb": 16,
        "status": "pending"
    }
}

if __name__ == "__main__":
    for name, info in cluster.items():
        print(f"{name} | {info['role']} | {info['ip']} | {info['status']}")
        