#!/usr/bin/env python3
import subprocess
import sys
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

console = Console()

def get_operator():
    name = input("Operator name: ")
    return name

def show_menu(operator):
    table = Table(box=box.SIMPLE, show_header=False, expand=True)
    table.add_column(justify="left", style="cyan")
    table.add_column(justify="left", style="white")
    
    table.add_row("1", "reporter     -system snapshot")
    table.add_row("2", "syswatch     - live monitor")
    table.add_row("3", "status       - operator dashboard")
    table.add_row("4", "netmap       - network scanner")
    table.add_row("5", "logwatch     - log monitor")
    table.add_row("6", "backup       - backup python folder")
    table.add_row("7", "ecfm         - research pipeline")
    table.add_row("8", "exit")
    
    console.print(Panel(table,
        title=f"[bold green]FRINGE COMMAND CENTER - {operator.upper()}[/bold green]",
        border_style="green"))
    
def main():
    subprocess.run('figlet FRINGE | lolcat', shell=True)
    operator = get_operator()
    
    while True:
        show_menu(operator)
        choice = input("Select: ")
        
        if choice == "1":
            subprocess.run(['reporter'])
        elif choice == "2":
            subprocess.run(['syswatch'])
        elif choice == "3":
            subprocess.run(['status'])
        elif choice == "4":
            subprocess.run(['sudo', 'netmap'])
        elif choice == "5":
            logfile = input("Log file path: ")
            subprocess.run(['logwatch', logfile])
        elif choice == "6":
            subprocess.run(['backup'])
        elif choice == "7":
            subprocess.run(['ecfm'])
        elif choice == "8":
            console.print("[cyan]Fringe out.[/cyan]")
            break
        else:
            console.print("[red]Invalid choice[/red]")

main()