#!/usr/bin/env python3
"""
sky_session.py - Fringe Cosmology observation logger
Logs telescope sessions to cosmo_log.json
"""
   
import json
import os
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

console = Console()

LOG_PATH = os.path.expanduser("~/python/cosmology/cosmo_log.json")

def load_log():
    """Load existing log or return empty list."""
    if os.path.exists(LOG_PATH):
        try:
            with open(LOG_PATH, 'r') as f:
                return json.load(f)
        except Exception:
            return []
    return[]

def save_log(entries):
    """Save log list to JSON file."""
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    with open(LOG_PATH, 'w') as f:
        json.dump(entries, f, indent=2)
        
def log_observation():
    """Interactive prompt to log a new observation session."""
    console.print(Panel(
        "[cyan]Log a new observation session.\nPress Enter to skip any optional field.[/cyan]",
        title="[bold cyan]NEW OBSERVATION[/bold cyan]",
        border_style='cyan'
    ))
    
    # Timestamp auto-set
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    target     = input("  Target object (required):").strip()
    if not target:
        console.print("[red]Target required. Aborting.[/red]")
        return
    
    scope      = input("  Scope / instrument (optional): ").strip() or "N/A"
    eyepiece   = input("  Eyepiece / magnification (optional): ").strip() or "N/A"
    conditions = input("  Sky conditions (optional); ").strip() or "N/A"
    seeing     = input("  seeing (1-5, 5=best) (optional): ").strip() or "N/A"
    notes      = input("  Notes (optional): ").strip() or ""
    
    entry = {
        "timestamp": timestamp,
        "target": target,
        "scope": scope,
        "eyepiece": eyepiece,
        "conditions": conditions,
        "seeing": seeing,
        "notes": notes
    }
    
    log = load_log()
    log.append(entry)
    save_log(log)
    
    console.print(Panel(
        f"[green]Session logged.[/green]\n"
        f"[dim]{timestamp} - {target}[/dim]",
        border_style="green",
    ))
    
def view_log():
    """Display all logged observation sessions."""
    log = load_log()
    
    if not log:
        console.print(Panel(
            "[yellow]No sessions logged yet.\nUse option 2 to log your first observation.[/yellow]",
            title="[yellow]EMPTY LOG[/yellow]",
            border_style="yellow"
        ))
        return
    
    console.print(f"\n[bold cyan]OBSERVATION LOG[/bold cyan] - [dim]{len(log)} session(s)[/dim]\n")
    
    # Show most recent first
    for i, entry in enumerate(reversed(log), 1):
        table = Table(box=box.SIMPLE, show_header=False, padding=(0, 2))
        table.add_column("Field", style="bold cyan", width=16)
        table.add_column("value", style="white")
        
        table.add_row("Target",     entry.get("target", "N/A"))
        table.add_row("Scope",      entry.get("scope", "N/A"))
        table.add_row("Eyepiece",   entry.get("eyepiece", "N/A"))
        table.add_row("Conditions", entry.get("seeing", "N/A"))
        table.add_row("Seeing",     entry.get("seeing", "N/A"))
        if entry.get("notes"):
            table.add_row("Notes", entry.get("notes"))
            
        console.print(Panel(
            table,
            title=f"[cyan]#{i} - {entry.get('timestamp', 'N/A')}[/cyan]",
            border_style="cyan",
            padding=(0, 1)
        ))