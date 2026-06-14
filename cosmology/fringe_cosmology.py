#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, '/home/ripple/python')
sys.path.insert(0, '/home/ripple/python/cosmology')

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box
import subprocess

console = Console()

def print_banner():
    subprocess.run('figlet -f slant "FRINGE" | /usr/games/lolcat', shell=True)
    subprocess.run('figlet -f small "COSMOLOGY" | /usr/games/lolcat', shell=True)

def print_menu():
    table = Table(box=box.SIMPLE, show_header=False, padding=(0, 2))
    table.add_column("Key", style="bold cyan", width=4)
    table.add_column("Option", style="white")
    table.add_column("Status", style="dim")
    
    table.add_row("1", "Query object", "Simbad / SDSS lookup")
    table.add_row("2", "Log observation session", "Sky log")
    table.add_row("3", "View session log", "Past observations")
    table.add_row("4", "Run analysis", "[dim yellow] Frank target - pending[/dim yellow]")
    table.add_row("5", "Scope control", "[dim yellow]Hardware target - pending[/dim yellow]")
    table.add_row("6", "Sky guide", "Constellations & planets")
    table.add_row("7", "Exit")
    
    console.print(Panel(
        table,
        title="[bold cyan]FRINGE COSMOLOGY[/bold cyan]",
        subtitle="[dim]dark sky research terminal[/dim]",
        border_style="cyan",
        padding=(1, 2)
    ))
    
def run_query():
    from sky_query import query_object
    console.print("\n[bold cyan]OBJECT QUERY[/bold cyan]", justify="center")
    console.print("[dim]Enter any onject name: galaxy, nebula, star, quasar...[/dim]\n")
    target = input("  Target: ").strip()
    if not target:
        console.print("[red]No target entered.[/red]")
        return
    console.print(f"\n[dim cyan]Querying Simbad for '{target}'...[/dim cyan]")
    query_object(target)
    
def log_session():
    from sky_session import log_observation
    log_observation()
    
def view_log():
    from sky_session import view_log as show_log
    show_log()
    
def analysis_stub():
    console.print(Panel(
        "[yellow]Deep analysis module is pending Frank coming online. \n\n"
        "Target HP Z840 - Dual Xeon E5-2699v4 - 256GB ECC RAM\n"
        "Planned: photometric pipeline, redshift analysis, spectra processing.[/yellow]",
        title="[yellow]Analysis - FRANK TARGET[/yellow]",
        border_style="yellow"
    ))
    
def scope_stub():
    console.print(Panel(
        "[yellow] Telescope control module pending hardware aquisition.\n\n"
        "Target: motorized equatorial mount with INDI/EKOS integration.\n"
        "Dark sky site: Bull shoals Lake, MArion County, AR.[/yellow]",
        title="[yellow]SCOPE CONTROL - HARDWARE PENDING[/yellow]",
        border_style="yellow"
    ))
    
def main():
    while True:
        try:
            print_banner()
            print_menu()
            choice = input("  Select option: ").strip()
            
            if choice == "1":
                run_query()
            elif choice == "2":
                log_session()
            elif choice == "3":
                view_log()
            elif choice == "4":
                analysis_stub()
            elif choice == "5":
                scope_stub()
            elif choice == "6":
                from sky_tonight import sky_menu
                sky_menu()   
            elif choice == "7":
                console.print("\n[dim cyan]Returning to Fringe...[/dim cyan]\n")
                break
            else:
                console.print("[red]Invalid option.[/red]")
                
            input("\n  [Enter to continue]")
            
        except KeyboardInterrupt:
            console.print("\n[dim cyan]Returning to Fringe...[/dim cyan]\n")
            break
if __name__ == "__main__":
    main()