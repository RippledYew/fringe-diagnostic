class FringeNode:
    def __init__(self, name, status, ip, role):
        self.name = name
        self.status = status
        self.ip = ip
        self.role = role
    def report(self):
        print(f"Node: {self.name} | Status: {self.status} | IP: {self.ip} | Role: {self.role}")
        
if __name__ == "__main__":
    acer = FringeNode("Acer", "online", "192.168.1.50", "Learn-to-code node")
    frank = FringeNode("Frank", "pending", "TBD", "Primary ECFM compute node")
    egor = FringeNode("Egor", "pending", "TBD", "Watchdog")
    print(acer.name)
    print(acer.status)
    acer.report()
    frank.report()
    egor.report()