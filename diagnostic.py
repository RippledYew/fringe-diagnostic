#!/usr/bin/env python3
import psutil
import subprocess
import os
import shutil
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

console = Console()

def get_operator():
    name = input("operator name: ")
    return name

def check_cpu():
    cpu = psutil.cpu_percent(interval=2)
    freq = psutil.cpu_freq()
    temps = {}
    try:
        temps = psutil.sensors_temperatures()
    except:
        pass
    return cpu, freq, temps

def check_ram():
    ram = psutil.virtual_memory()
    swap = psutil.swap_memory()
    return ram, swap

def check_disk():
    partitions = psutil.disk_partitions()
    results = []
    for p in partitions:
        if p.mountpoint.startswith('/snap'):
            continue
        try:
            usage = psutil.disk_usage(p.mountpoint)
            results.append({
                'mount' : p.mountpoint,
                'total': round(usage.total / (1024**3), 1),
                'used' : round(usage.used / (1024**3), 1),
                'percent': usage.percent
            })
        except:
            pass
    return results

def check_network():
    result = subprocess.run(
        ['ping', '-c', '3', '8.8.8.8'],
        capture_output=True, text=True
    )
    if 'avg' in result.stdout:
        avg = result.stdout.split('/')[-3].split('/')[-1]
        return f"{avg}ms avg"
    return "UNREACHABLE"

def check_toolkit():
    tools = ['reporter', 'syswatch', 'status', 'netmap',
             'logwatch', 'backup', 'ecfm', 'pingfringe',
             'fringe', 'diagnostic']
    results = []
    for tool in tools:
        path = f'/usr/local/bin/{tool}'
        exists = os.path.exists(path)
        executable = os.access(path, os.X_OK) if exists else False
        results.append({
            'tool': tool,
            'status': 'OK' if executable else 'MISSING'
        })
    return results

def check_top_processes():
    procs = []
    for p in psutil.process_iter(['pid', 'name', 'memory_percent']):
        try:
            cpu = p.cpu_percent(interval=0.1)
            info = p.info
            info['cpu_percent'] = cpu
            if info['pid'] > 100 and info['name'] not in ['kthreadd']:
                procs.append(info)
        except:
            pass
    sorted_procs = sorted(procs, key=lambda x: x['memory_percent'], reverse=True)
    return sorted_procs[:5]

def check_gpu():
    try:
        vendor = open('/sys/class/drm/card1/device/vendor').read().strip()
        power = open('/sys/class/drm/card1/device/power_state').read().strip()
        enable = open('/sys/class/drm/card1/device/enable').read().strip()
        if vendor == '0x8086':
            return {
                'name': 'Intel HD Graphics 620',
                'power': power,
                'status': 'ENABLED' if enable == '1' else 'DISABLED'
            }
    except:
        pass
    return None

def display_report(operator, cpu, freq, temps, ram, swap, disks, ping, toolkit, procs, uptime, gpu):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    subprocess.run('figlet DIAGNOSTIC | lolcat', shell=True)
    console.print(Panel(
        f"[cyan]Operator:[/cyan] {operator.upper()}   [cyan]Time:[/cyan] {now}  [cyan]Uptime:[/cyan] {uptime}",
        title="[bold green]FRINGE DIAGNOSTIC REPORT[/bold green]",
        box=box.DOUBLE
    ))
    cpu_color = "green" if cpu < 70 else "yellow" if cpu < 90 else "red"
    console.print(Panel(
        f"[{cpu_color}]Usage: {cpu}%[/{cpu_color}]  "
        f"[cyan]Freq: {round(freq.current)}MHz[/cyan]  ",
        title="[bold]CPU[/bold]",
        box=box.SIMPLE
        ))
    if temps:
        temp_lines = []
        for chip, entries in temps.items():
            for entry in entries:
                if not entry.label:
                    continue
                temp_color = "green" if entry.current < 70 else "yellow" if entry.current < 90 else "red"
                temp_lines.append(f"[{temp_color}]{entry.label}: {entry.current}°C[/{temp_color}]")
        console.print(Panel(
            "   ".join(temp_lines),
            title="[bold]TEMPS[/bold]",
            box=box.SIMPLE
        ))
    ram_color = "green" if ram.percent < 70 else "yellow" if ram.percent < 90 else "red"
    swap_color = "green" if swap.percent < 50 else "yellow" if swap.percent < 80 else "red"
    console.print(Panel(
        f"[{ram_color}]RAM: {round(ram.used / (1024**3), 1)}GB / {round(ram.total / (1024**3), 1)}GB ({ram.percent}%)[/{ram_color}]   "
        f"[{swap_color}]Swap: {round(swap.used / (1024**3), 1)}GB / {round(swap.total / (1024**3), 1)}GB ({swap.percent}%)[/{swap_color}]",
        title="[bold]MEMORY[/bold]",
        box=box.SIMPLE
    ))
    disk_table = Table(title="DISK", box=box.SIMPLE, show_header=True)
    disk_table.add_column("[bold]MOUNT[/bold]", style="cyan")
    disk_table.add_column("[bold]TOTAL[/bold]", style="white")
    disk_table.add_column("[bold]USED[/bold]", style="white")
    disk_table.add_column("[bold]STATUS[/bold]", style="green")
    for d in disks:
        disk_color = "green" if d['percent'] < 70 else "yellow" if d['percent'] < 90 else "red"
        disk_table.add_row(
            d['mount'],
            f"{d['total']}GB",
            f"{d['used']}GB",
            f"[{disk_color}]{d['percent']}%[/{disk_color}]"
        )
    console.print(disk_table)
    ping_color = "green" if "ms" in ping else "red"
    console.print(Panel(
        f"[{ping_color}]Starlink: {ping}[/{ping_color}]",
        title="[bold]NETWORK[/bold]",
        box=box.SIMPLE
    ))
    toolkit_table = Table(title="FRINGE TOOLKIT", box=box.SIMPLE, show_header=True)
    toolkit_table.add_column("[bold]COMMAND[/bold]", style="cyan")
    toolkit_table.add_column("[bold]STATUS[/bold]", style="white")
    for t in toolkit:
        status_color = "green" if t['status'] == 'OK' else "red"
        toolkit_table.add_row(
            t['tool'],
            f"[{status_color}]{t['status']}[/{status_color}]"
        )
    console.print(toolkit_table)
    proc_table = Table(title="TOP PROCESSES", box=box.SIMPLE, show_header=True)
    proc_table.add_column("[bold]PID[/bold]", style="cyan")
    proc_table.add_column("[bold]NAME[/bold]", style="white")
    proc_table.add_column("[bold]CPU%[/bold]", style="green")
    proc_table.add_column("[bold]MEM%[/bold]", style="magenta")
    for p in procs:
        proc_table.add_row(
            str(p['pid']),
            p['name'],
            f"{p['cpu_percent']}%",
            f"{round(p['memory_percent'], 1)}%"
        )
    console.print(proc_table)    
        
    if gpu:
        console.print(Panel(
            f"[cyan]{gpu['name']}[/cyan]   "
            f"[green]Power: {gpu['power']}[/green]   "
            f"[green]{gpu['status']}[/green]",
            title="[bold]GPU[/bold]",
            box=box.SIMPLE
        ))
   
    
    summary = check_summary(cpu, ram, disks, ping, temps)
    summary_line = "  ".join(
        f"[{'green' if v == 'OK' else 'red'}]{k}: {v}[/{'green' if v == 'OK'else 'red'}]"
         for k, v in summary.items()
    )
    console.print(Panel(summary_line, title="[bold]SYSTEM STATUS[/bold]", box=box.DOUBLE))
    
def check_uptime():
    boot = psutil.boot_time()
    uptime_seconds = datetime.now().timestamp() - boot
    hours = int(uptime_seconds // 3600)
    minutes = int((uptime_seconds % 3600) // 60)
    return f"{hours}h {minutes}m"
  
def main():
    operator = get_operator()
    console.print("[cyan] Running diagnostics...[/cyan]")
    cpu, freq, temps = check_cpu()
    ram, swap = check_ram()
    uptime = check_uptime()
    disks = check_disk()
    ping = check_network()
    toolkit = check_toolkit()
    procs = check_top_processes()
    gpu = check_gpu()
    display_report(operator, cpu, freq, temps, ram, swap, disks, ping, toolkit, procs, uptime, gpu)
    
def check_summary(cpu, ram, disks, ping, temps):
    results = {}
    results['CPU'] = "OK" if cpu < 90 else "WARN"
    results['RAM'] = "OK" if ram.percent < 90 else "WARN"
    results['DISK'] = "OK" if all(d['percent'] < 90 for d in disks) else "WARN"
    results['NETWORK'] = "OK" if "ms" in ping else "FAIL"
    if temps:
        hot = any(e.current >= 90 for entries in temps.values() for e in entries)
        results['TEMPS'] = "WARN" if hot else "OK"
    else:
        results['TEMPS'] = "N/A"
    return results

main()