from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

console = Console()

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
        table = Table(box=box.SIMPLE, show_header=False, expand=True)
        table.add_column(justify="left", style="cyan")
        table.add_column(justify="left", style="white")
        table.add_row("Name", self.name)
        status_color = "green" if self.is_online() else "yellow"
        table.add_row("Status", f"[{status_color}]{self.status}[/{status_color}]")
        table.add_row("IP", self.ip)
        table.add_row("Role", self.role)
        table.add_row("OS", self.os)
        table.add_row("CPU", self.cpu)
        table.add_row("Cores", str(self.cores))
        table.add_row("RAM", f"{self.ram_gb}GB")
        console.print(Panel(table, title=f"[bold green]{self.name}[/bold green]", border_style="green"))
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
        
def demo():
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


if __name__ == "__main__":
    demo()