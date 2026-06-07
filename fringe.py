#!/usr/bin/env python3
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box
from fringe_nodes import cluster

console = Console()

def get_operator():
    name = input("Operator name: ")
    return name

def show_menu(operator):
    table = Table(box=box.SIMPLE, show_header=False, expand=True)
    table.add_column(justify="left", style="cyan")
    table.add_column(justify="left", style="white")
    
    table.add_row("1", "reporter       -system snapshot")
    table.add_row("2", "syswatch       - live monitor")
    table.add_row("3", "status         - operator dashboard")
    table.add_row("4", "netmap         - network scanner")
    table.add_row("5", "logwatch       - log monitor")
    table.add_row("6", "backup         - backup python folder")
    table.add_row("7", "ecfm           - research pipeline")
    table.add_row("8", "pingfringe     - cluster ping scan")
    table.add_row("9", "cluster report - node details")
    table.add_row("10", "exit")
    
    node_table = Table(box=box.SIMPLE, show_header=False, expand=True)
    node_table.add_column(justify="left", style="green")
    node_table.add_column(justify="left", style="cyan")
    node_table.add_column(justify="right", style="white")
    
    for name, info in cluster.items():
        node_table.add_row(name, info.role, info.status)
        
    console.print(Panel(node_table,
        title="[bold green]CLUSTER STATUS[/bold green]",
        border_style="green"))
    
    console.print(Panel(table,
        title=f"[bold green]FRINGE COMMAND CENTER - {operator.upper()}[/bold green]",
        border_style="green"))
    
def main():
    subprocess.run('figlet FRINGE | /usr/games/lolcat', shell=True)
    operator = get_operator()

    while True:
        show_menu(operator)
        choice = input("Select: ")
        
        if choice == "1":
            subprocess.run(['reporter'])
        elif choice == "2":
            try:
                subprocess.run(['syswatch'])
            except KeyboardInterrupt:
                pass
        elif choice == "3":
            try:
                subprocess.run(['status'])
            except KeyboardInterrupt:
                pass
        elif choice == "4":
            subprocess.run(['sudo', 'netmap'])
        elif choice == "5":
            try:
                logfile = input("Log file path: ")
                subprocess.run(['logwatch', logfile])
            except KeyboardInterrupt:
                console.print("[cyan]Logwatch Closed. [/cyan]")
        elif choice == "6":
            subprocess.run(['backup'])
        elif choice == "7":
            subprocess.run(['ecfm'])
        elif choice == "8":
            subprocess.run(['pingfringe'])
        elif choice == "9":
            for name, node in cluster.items():
                node.report()
        elif choice == "10":
            console.print("[cyan]Fringe out.[/cyan]")
            break
        else:
            console.print("[red]Invalid choice[/red]")


if __name__ == "__main__":
    main()