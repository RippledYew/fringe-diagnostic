class FringeNode:
    def __init__(self, name, status, ip, role, os, cpu, cores, ram_gb):
        self.name = name
        self.status = status
        self.ip = ip
        self.role = role
        self.os = os
        self.cpu = cpu
        self.cores = cores
        self.ram_gb = ram_gb
    def report(self):
        print(f"Node: {self.name} | Status: {self.status} | IP: {self.ip}")
        print(f"Role: {self.role} | OS: {self.os} | Cores: {self.cores} | RAM: {self.ram_gb}GB")
    def is_online(self):
        return self.status == "online"
    def ping(self):
        if self.ip == "TBD":
            return f"{self.name} - IP not assigned yet"
        import subprocess
        result = subprocess.run(['ping', '-c', '1', self.ip], capture_output=True)
        if result.returncode == 0:
            return f"{self.name} - reachable"
        else:
            return f"{self.name} - unreachable"
        
if __name__ == "__main__":
    acer = FringeNode("Acer", "online", "192.168.1.50", "learn", "ubuntu 22.04", "intel if-7200U", 4, 16)
    frank = FringeNode("Frank", "pending", "TBD", "compute", "ubuntu 24.04", "Dual Xeon e5-2699 v4", 44, 256)
    egor = FringeNode("Egor", "pending", "TBD", "watchdog", "armbian", "RK3588S", 8, 32)
    print(acer.name)
    print(acer.status)
    print(acer.ping())
    print(frank.ping())
    print(egor.ping())
    acer.report()
    frank.report()
    egor.report()