#!/usr/bin/env python3
import subprocess
import sys
from rich.console import Console
from rich.table import Table
from rich import box

console = Console()

def get_operator():
    name = input("Operator name: ")
    return name

def scan_network():
    return "10.58.163.0/24"

def run_scan(subnet):
    result = subprocess.run(
        ['nmap', '-sn', subnet],
        capture_output=True, text=True
    )
    return result.stdout

def parse_results(raw):
    devices = []
    current = {}
    for line in raw.split('\n'):
        if 'Nmap scan report' in line:
            if current:
                devices.append(current)
            current = {'host': line.split()[-1]}
        elif "MAC Address" in line:
            parts = line.split('(')
            current['mac'] = parts[0].split()[-1]
            current['vendor'] = parts[1].replace(')', '').strip() if len(parts) > 1 else 'Unknown'
        elif 'host is up' in line:
            current['status'] = 'UP'
    if current:
        devices.append(current)
    return devices
    
def display(devices, operator, subnet):
    table = Table(
        title=f'[bold green]FRINGE NETMAP - {operator.upper()} - {subnet}[/bold green]',
        box=box.SIMPLE,
        show_header=True
    )
    table.add_column("[bold]HOST[/bold]", style="cyan")
    table.add_column('[bold]STATUS[/bold]', style="green")
    table.add_column("[bold]MAC[/bold]", style="white")
    table.add_column("[bold]VENDOR[/bold]", style="magenta")
    
    for d in devices:
        table.add_row(
            d.get('host', '?'),
            d.get('status', 'UP'),
            d.get('mac', 'N/A'),
            d.get('vendor', 'N/A')
        )
    console.print(table)
    
def main():
    subprocess.run('figlet FRINGE | lolcat', shell=True)
    operator = get_operator()
    console.print("[cyan]Scanning network...[/cyan]")
    subnet = scan_network()
    if not subnet:
        console.print("[red]Could not detect subnet[/red]")
        sys.exit(1)
    raw = run_scan(subnet)
    devices = parse_results(raw)
    display(devices, operator, subnet)
    
main()
    