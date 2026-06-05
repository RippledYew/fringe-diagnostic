#!/usr/bin/env python3
import sys
import time
import subprocess
from rich.console import Console
from rich.panel import Panel
from rich import box

console = Console()

def get_operator():
    name = input("Operator name: ")
    return name

def watch_log(logfile, operator):
    subprocess.run('figlet FRINGE | lolcat', shell=True)
    console.print(Panel(
        f"[cyan]Watching:[/cyan] [white]{logfile}[/white]\n[cyan]Operator:[/cyan] [white]{operator}[/white]",
        title="[bold green]FRINGE LOGWATCH[/bold green]",
        border_style="green"
    ))
    try:
        with open(logfile, 'r') as f:
            f.seek(0, 2)
            while True:
                line = f.readline()
                if line:
                    line = line.strip()
                    if 'error' in line.lower() or 'fail' in line.lower():
                        console.print(f'[red]{line}[/red]')
                    elif 'warn' in line.lower():
                        console.print(f'[yellow]{line}[/yellow]')
                    else:
                        console.print(f"[green]{line}[/green]")
                else:
                    time.sleep(0.5)
    except FileNotFoundError:
        console.print(f"[red]Log file not found: {logfile}[/red]")
        sys.exit(1)
    except KeyboardInterrupt:
        console.print("[cyan]Logwatch closed. [/cyan]")
          
def main():
    operator = get_operator()
    if len(sys.argv) < 1:
        logfile = sys.argv[1]
    else:
        logfile = input("Log file path: ")
    watch_log(logfile, operator)
    
main()