#!/usr/bin/env python3
import psutil
import time
import subprocess
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import BarColumn, Progress, TextColumn
from rich.layout import Layout
from rich.live import Live
from rich import box

console = Console()

def get_operator():
    name = input("operator name: ")
    return name

def cpu_color(val):
    if val < 50:
        return "cyan"
    elif val < 80:
        return "yellow"
    return "red"
    
def make_dashboard(operator):
        table = Table(box=box.SIMPLE, show_header=False, expand=True)
        table.add_column(justify="left")
        table.add_column(justify="right")
        
        # CPU
        cpu = psutil.cpu_percent(interval=1)
        c = cpu_color(cpu)
        table.add_row (f"[bold]CPU[/bold]", f"[{c}]{cpu}%[/{c}]")
        
        # RAM
        ram = psutil.virtual_memory()
        ram_used = round(ram.used / (1024 ** 3), 1)
        ram_total = round(ram.total / (1024 ** 3), 1)
        ram_pct = ram.percent
        ram_color = cpu_color(ram_pct)
        table.add_row("[bold]RAM[/bold]",
                      f"[{ram_color}]{ram_used}GB / {ram_total}GB ({ram_pct}%)[/{ram_color}]")
        
        # Disk
        partitions = psutil.disk_partitions()
        for p in partitions:
            if '/snap' in p.mountpoint:
                continue
            usage = psutil.disk_usage(p.mountpoint)
            total = round(usage.total / (1024 ** 3), 1)
            used = round(usage.used / (1024 ** 3), 1)
            pct = usage.percent
            d_color = cpu_color(pct)
            table.add_row(f"[bold]DISK {p.mountpoint}[/bold]",
                          f"[{d_color}]{used}GB / {total}GB ({pct}%)[/{d_color}]")
            
        # Network 
        net = psutil.net_io_counters()
        sent = round(net.bytes_sent / (1024 ** 2), 1)
        recv = round(net.bytes_recv / (1024 ** 2), 1)
        table.add_row("[bold]NET SENT[/bold]", f"[cyan]{sent} MB[/cyan]")
        table.add_row("[bold]NET RECV[/bold]", f"[cyan]{recv} MB[/cyan]")
        
        # Uptime
        boot = datetime.fromtimestamp(psutil.boot_time())
        uptime = datetime.now() - boot
        hours, rem = divmod(int(uptime.total_seconds()), 3600)
        minutes = rem // 60
        table.add_row("[bold]UPTIME[/bold]",
                      f"[magenta]{hours}h {minutes}m[/magenta]")
        
        # Timestamp
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        table.add_row("[bold]UPDATED[/bold]", f"[white]{now}[/white]")
        
        return Panel(table,
                     title=f"[bold green] FRINGE NODE - {operator.upper()}[/bold green]",
                        border_style="green")
        
def main():
    subprocess.run('figlet FRINGE | lolcat', shell=True)
    operator = get_operator()
                   
    with Live(make_dashboard(operator), refresh_per_second=1) as live:
          while True:
            time.sleep(2)
            live.update(make_dashboard(operator))
            
main()