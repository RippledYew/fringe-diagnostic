#!/usr/bin/env python3
"""
sky_query.py - Fringe Cosmology object lookup
uses astroquery to pull real data from Simbad and SDSS.
"""

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

console = Console()

def query_object(target):
    """
    Query Simbad for a named object and display results in a Rich panel.
    Falls back with a clear error if astroquery isn't installed.
    """
    try:
        from astroquery.simbad import Simbad
        from astropy.coordinates import SkyCoord
        import astropy.units as u
    except ImportError:
        console.print(Panel(
            "[red]astroquery not installed.\n\n"
            "Run[/red] [bold white]pip3 install astroquery astropy --break-system-packages[/bold white]",
            title="[red]MISSING DEPENDENCY[/red]",
            border_style="red"
        ))
        return
    
    try:
        result = Simbad.query_object(target)
    except Exception as e:
        console.print(f"[red]Query failed: {e}[/red]")
        return
    
    if result is None:
        console.print(Panel(
            f"[yellow]No results found for '{target}'.\n"
            "Try alternate names (e.g. 'M31' vs 'Andromeda Galaxy', 'NGC 224').[yellow]",
            title="[yellow]NOT FOUND[/yellow]",
            border_style="yellow"
        ))
        return
        
    # Pull row 0 - primary match
    r = result[0]
    
    # Helper to safely extract a value or return'N/A'
    def get(field):
        try:
            val = result[field][0]
            if val is None or str(val).strip() in ('', '--', 'nan', 'None'):
                return "N/A"
            return str(val).strip()
        except Exception:
            return "N/A"
    
    # Parse coordinates
    ra = get('ra')
    dec = get('dec')
    
    # Try to build galactic coords from RA/Dec
    galactic = "N/A"
    try:
        if ra != "N/A" and dec != "N/A":
            coord = SkyCoord(ra=ra, dec=dec, unit=(u.deg, u.deg), frame='icrs')
            gal = coord.galactic
            galactic = f"l={gal.l.deg:.4f}° b={gal.b.deg:.4f}°"
    except Exception:
        pass
    
    # Build display table
    table = Table(box=box.SIMPLE, show_header=False, padding=(0, 2))
    table.add_column("field", style="bold cyan", width=22)
    table.add_column("Value", style="white")
    
    table.add_row("Matched ID", get('matched_id'))
    table.add_row("Object name", get('main_id'))
    table.add_row("RA(J200)", ra)
    table.add_row("Dec (J2000)", dec)
    table.add_row("Galactic coords", galactic)
    
    console.print(Panel(
        table,
        title=f"[bold cyan]SIMBAD - {target.upper()}[/bold cyan]",
        subtitle="[dim]astroquery.simbad[/dim]",
        border_style="cyan",
        padding=(1, 2)
    ))