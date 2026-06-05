#!/usr/bin/env python3
import subprocess
import sys
sys.path.insert(0, '/home/ripple/python')
from fringe_nodes import cluster
from rich.console import Console
from rich.table import Table
from rich import box

console = Console()

def ping(ip):
    if ip == "TBD":
        return "pending"
    result = subprocess.run(
        ['ping', '-c', '1', '-W', '1', ip],
        capture_output=True, text=True
    )
    return "online" if result.returncode == 0 else "unreachable"

def scan_cluster():
    subprocess.run('figlet FRINGE | lolcat', shell=True)
    
    table = Table(
        title="[bold green]FRINGE CLUSTER PING SCAN[/bold green]",
        box=box.SIMPLE,
        show_header=True
    )
    table.add_column("[bold]NODE[/bold]", style="cyan")
    table.add_column("[bold]ROLE[/bold]", style="white")
    table.add_column("[bold]IP[/bold]", style="white")
    table.add_column("[bold]STATUS[/bold]", style="white")
    
    for name, info in cluster.items():
        console.print(f"[cyan]Pinging {name}...[/cyan]")
        status = ping(info.ip)
        if status == "online":
            color = "green"
        elif status == "pending":
            color = "yellow"
        else:
            color = "red"
        table.add_row(
            name,
            info.role,
            info.ip,
            f"[{color}]{status}[/{color}]"
        )
        
    console.print(table)
    
scan_cluster()