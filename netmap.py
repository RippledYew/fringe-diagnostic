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
    result = subprocess.run(
        ['ip', 'route', 'show', 'default'],
        capture_output=True, text=True
    )
    for line in result.stdout.split('\n'):
        if 'default' in line:
            parts = line.split()
            for i, part in enumerate(parts):
                if part == 'dev':
                    iface = parts[i + 1]
                    # get IP of that interface
                    ip_result = subprocess.run(
                        ['ip', '-4', 'addr', 'show', iface],
                        capture_output=True, text=True
                    )
                    for ip_line in ip_result.stdout.split('\n'):
                        if 'inet ' in ip_line:
                            cidr = ip_line.strip().split()[1]
                            octets = cidr.rsplit('.', 1)
                            return octets[0] + '.0/24'
    return None

def run_scan(subnet):
    result = subprocess.run(
        ['sudo', 'arp-scan', '--localnet'],
        capture_output=True, text=True
    )
    return result.stdout

def parse_results(raw):
    devices = []
    for line in raw.split('\n'):
        parts = line.split('\t')
        if len(parts) >= 3:
            ip = parts[0].strip()
            mac = parts[1].strip()
            vendor = parts[2].strip()
            if ip.startswith('192.168') and ':' in mac:
                devices.append({
                    'host': ip,
                    'status': 'UP',
                    'mac': mac,
                    'vendor': vendor
                })
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
    subprocess.run('figlet FRINGE | /usr/games/lolcat', shell=True)
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
    