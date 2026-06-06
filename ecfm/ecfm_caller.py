#! /usr/bin/env python3
import sys
import os
sys.path.insert(0, '/home/ripple/python/ecfm')

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box
import subprocess

console = Console()

subprocess.run('figlet FRINGE | lolcat', shell=True)

while True:
    table = Table(box=box.SIMPLE, show_header=False, expand=True)
    table.add_column(justify="left", style="cyan")
    table. add_column(justify="left", style="white")
    table.add_row("1", "smoke test          - engine health check")
    table.add_row("2", "divergence sweep    - bounded crossing arc")
    table.add_row("3", "deep geometry       - 200k steps [frank target]")
    table.add_row("4", "view reports        - probe log reader")
    table.add_row("5", "check ecfm folder   - directory listing")
    table.add_row("6", "exit")
    console.print(Panel(table, title="[bold green] ECFM RESEARCH PIPELINE[/bold green]", border_style="green"))

    choice = input("Select: ")
    if choice == "1":
        from ecfm_runner import run_probe, summarize
        r = run_probe({"probe_id": "smoke_01", "probe_name": "smoke",
                       "N": 28, "etz": 0.75, "seed": 0, "steps": 400})
        console.print(f"[green]{summarize(r)}[/green]")
     
    elif choice == "2":
        from ecfm_runner import run_probe, summarize
        console.print("[cyan]Running bounded divergence sweep...[/cyan]")
        steps_list = [5000, 10000, 15000, 20000, 25000, 30000, 35000, 40000, 45000, 50000]
        for i, s in enumerate(steps_list):
            console.print(f"[yellow]Running step {s}...[/yellow]")
            r = run_probe({"probe_id": f"sweep_{i}", "probe_name": "divergence_sweep",
                           "N": 28, "eta": 0.75, "seed": 0, "steps": s})
            console.print(f"[green]{summarize(r)}[/green]")
        console.print("[cyan]Sweep complete.[/cyan]")
        
    elif choice == "3":
        console.print("[yellow]Deep geometry run - 200k steps[/yellow]")
        console.print("[yellow]Frank target - not yet available on Acer[/yellow]")
        console.print("[cyan]This probe will run when Frank is online.[/cyan]")
        
    elif choice == "4":
        subprocess.run(['python3', '/home/ripple/python/ecfm/ecfm_runner.py'])
        
    elif choice == "5":
        subprocess.run(['ls', '-1h', '/home/ripple/python/ecfm/'])
        
    elif choice == "6":
        console.print("[cyan]ECFM pipeline closed.[/cyan]")
        break
    
    else:
        console.print("[red]Invalid choice[/red]")