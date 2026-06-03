#!/usr/bin/env python3
import os
import subprocess
import sys
from datetime import datetime
from rich.console import Console
from rich import box

console = Console()

def get_operator():
    name = input("Operator name: ")
    return name

def run_backup():
    subprocess.run('figlet FRINGE | lolcat', shell=True)
    operator = get_operator()
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"fringe_backup_{timestamp}.tar.gz"
    backup_path = f"/home/ripple/{backup_name}"
    source = "/home/ripple/python"
    
    console.print(f"[cyan]Backing up:[/cyan] [white]{source}[/white]")
    console.print(f"[cyan]Saving to:[/cyan] [white]{backup_path}[/white]")
    
    result = subprocess.run(
        ['tar', '-czf', backup_path, source],
        capture_output=True, text=True
    )
    
    if result.returncode == 0:
        size = os.path.getsize(backup_path)
        size_mb = round(size / 1024**2, 2)
        console.print(f"[green]Backup complete! Size: {size_mb}MB[/green]")
        console.print(f"[green]Saved: {backup_name}[/green]")
    else:
        console.print(f"[red]Backup failed![/red]")
        console.print(f"[red]{result.stderr}[/red]")
        
run_backup()