#!/usr/bin/env python3
"""
sky_tonight.py — Fringe Cosmology sky guide
Shows visible constellations and planets for tonight
from Fringe Labs, Marion County AR.
"""

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box
from datetime import datetime

console = Console()

# --- Fringe Labs observer location ---
FRINGE_LAT  =  36.3717   # degrees North
FRINGE_LON  = -92.5849   # degrees West
FRINGE_ELEV =  210       # meters
FRINGE_NAME = "Fringe Labs — Marion County, AR"

# --- Constellation data ---
# Each entry: name, RA center (hours), Dec center (degrees), 
# best month visible, mythology blurb, main stars
CONSTELLATIONS = {
    "Orion": {
        "ra": 5.5, "dec": 5.0,
        "best_month": 1,
        "stars": ["Betelgeuse", "Rigel", "Bellatrix", "Mintaka", "Alnilam", "Alnitak", "Saiph"],
        "myth": "The great hunter of Greek mythology. Orion boasted he could kill any creature on Earth. The scorpion Scorpius was sent to humble him — which is why they appear on opposite sides of the sky.",
        "notes": "Contains the famous Orion Nebula (M42) in his sword. Betelgeuse is a red supergiant that may go supernova."
    },
    "Cassiopeia": {
        "ra": 1.0, "dec": 60.0,
        "best_month": 11,
        "stars": ["Schedar", "Caph", "Gamma Cas", "Ruchbah", "Segin"],
        "myth": "Queen of Ethiopia in Greek myth, punished for her vanity by being tied to her throne and spinning around the pole star forever.",
        "notes": "Circumpolar from your location — visible every clear night all year. Distinctive W or M shape depending on time of year."
    },
    "Ursa Major": {
        "ra": 10.7, "dec": 55.0,
        "best_month": 4,
        "stars": ["Dubhe", "Merak", "Phecda", "Megrez", "Alioth", "Mizar", "Alkaid"],
        "myth": "Zeus transformed Callisto into a bear to protect her from Hera's jealousy, then placed her in the sky. The Big Dipper is her body and tail.",
        "notes": "Circumpolar from your location. Dubhe and Merak are the pointer stars to Polaris. Mizar has a naked-eye companion called Alcor."
    },
    "Ursa Minor": {
        "ra": 15.0, "dec": 77.0,
        "best_month": 6,
        "stars": ["Polaris", "Kochab", "Pherkad", "Yildun", "Epsilon UMi", "Zeta UMi", "Eta UMi"],
        "myth": "Arcas, son of Callisto, placed in the sky beside his mother by Zeus. Contains Polaris, the North Star.",
        "notes": "Polaris sits within 1 degree of true north and barely moves all night. Kochab was the pole star 3000 years ago."
    },
    "Leo": {
        "ra": 10.5, "dec": 15.0,
        "best_month": 4,
        "stars": ["Regulus", "Denebola", "Algieba", "Zosma", "Chertan", "Adhafera", "Eta Leo"],
        "myth": "The Nemean Lion slain by Hercules as his first labor. Zeus honored the beast by placing it among the stars.",
        "notes": "Regulus sits almost exactly on the ecliptic — planets and the Moon pass very close to it. The Leonid meteor shower radiates from here every November."
    },
    "Scorpius": {
        "ra": 16.5, "dec": -26.0,
        "best_month": 7,
        "stars": ["Antares", "Shaula", "Sargas", "Dschubba", "Graffias", "Lesath", "Girtab"],
        "myth": "The scorpion sent by Gaia to slay Orion. The gods placed them on opposite sides of the sky so they never meet.",
        "notes": "Antares is a massive red supergiant — its name means rival of Mars because of its red color. Low on southern horizon from Arkansas."
    },
    "Cygnus": {
        "ra": 20.6, "dec": 44.0,
        "best_month": 9,
        "stars": ["Deneb", "Albireo", "Sadr", "Gienah Cygni", "Delta Cyg"],
        "myth": "Zeus disguised as a swan, or Orpheus transformed after death. The Northern Cross asterism is prominent.",
        "notes": "Deneb is one of the most luminous stars known — if it were as close as Sirius it would cast shadows at night. Albireo is a beautiful gold and blue double star."
    },
    "Lyra": {
        "ra": 18.9, "dec": 36.0,
        "best_month": 8,
        "stars": ["Vega", "Sheliak", "Sulafat", "Delta Lyr", "Epsilon Lyr"],
        "myth": "The lyre of Orpheus, placed in the sky after his death. His music was so beautiful it could move rocks and trees.",
        "notes": "Vega is the brightest star in the summer sky and the second brightest in the northern hemisphere. Contains the famous Ring Nebula (M57)."
    },
    "Aquila": {
        "ra": 19.7, "dec": 3.0,
        "best_month": 8,
        "stars": ["Altair", "Tarazed", "Okab", "Delta Aql", "Lambda Aql"],
        "myth": "The eagle of Zeus, who carried his thunderbolts. Also the eagle that tormented Prometheus.",
        "notes": "Altair rotates so fast it bulges at the equator — a day there is only 9 hours long. Part of the Summer Triangle with Vega and Deneb."
    },
    "Perseus": {
        "ra": 3.5, "dec": 45.0,
        "best_month": 12,
        "stars": ["Mirfak", "Algol", "Zeta Per", "Epsilon Per", "Delta Per"],
        "myth": "The hero who slew Medusa and rescued Andromeda. Algol represents the eye of Medusa.",
        "notes": "Algol is a famous eclipsing binary — it dims noticeably every 2.87 days as one star passes in front of the other. The Perseid meteor shower radiates from here every August."
    },
    "Andromeda": {
        "ra": 1.0, "dec": 38.0,
        "best_month": 11,
        "stars": ["Alpheratz", "Mirach", "Almach", "Delta And", "Pi And"],
        "myth": "Princess chained to a rock as sacrifice to the sea monster Cetus, rescued by Perseus.",
        "notes": "Contains the Andromeda Galaxy (M31) — the most distant object visible to the naked eye at 2.5 million light years. You queried it earlier today."
    },
    "Gemini": {
        "ra": 7.0, "dec": 22.0,
        "best_month": 2,
        "stars": ["Castor", "Pollux", "Alhena", "Wasat", "Mebsuda", "Mekbuda", "Propus"],
        "myth": "The twin brothers Castor and Pollux, sons of Leda. When Castor was killed, Pollux shared his immortality so they could remain together.",
        "notes": "Pollux is actually brighter than Castor despite being Beta Geminorum. Castor is actually a sextuple star system — six stars bound together."
    },
    "Bootes": {
        "ra": 14.7, "dec": 31.0,
        "best_month": 6,
        "stars": ["Arcturus", "Izar", "Muphrid", "Seginus", "Delta Boo"],
        "myth": "The herdsman or bear driver, following Ursa Major around the pole. Some say he invented the plow.",
        "notes": "Arcturus is the brightest star in the northern hemisphere and the fourth brightest overall. It has a distinctly orange color visible to the naked eye."
    },
    "Virgo": {
        "ra": 13.4, "dec": -4.0,
        "best_month": 5,
        "stars": ["Spica", "Zavijava", "Porrima", "Auva", "Vindemiatrix"],
        "myth": "Demeter, goddess of the harvest, mourning her daughter Persephone. When she grieves, crops fail and winter comes.",
        "notes": "Spica is a close binary where both stars are distorted into egg shapes by mutual gravity. The Virgo Cluster of galaxies lies here — over 1300 galaxies."
    },
}

# --- Planet data (approximate, for educational display) ---
PLANETS = {
    "Mercury": {
        "type": "Terrestrial",
        "distance_au": 0.39,
        "diameter_km": 4879,
        "moons": 0,
        "day_hours": 1407.6,
        "year_days": 88,
        "fact": "A year on Mercury is shorter than a day on Mercury. It rotates so slowly that the Sun rises, stops, goes backward, then continues — from some spots on the surface.",
        "visibility": "Only visible near sunrise or sunset, never far from the Sun. Look low on the horizon."
    },
    "Venus": {
        "type": "Terrestrial",
        "distance_au": 0.72,
        "diameter_km": 12104,
        "moons": 0,
        "day_hours": 5832,
        "year_days": 225,
        "fact": "Venus rotates backwards compared to most planets. If you stood on Venus, the Sun would rise in the west. Its surface is hot enough to melt lead.",
        "visibility": "The brightest object in the sky after the Sun and Moon. Evening or morning star depending on its orbit position."
    },
    "Mars": {
        "type": "Terrestrial",
        "distance_au": 1.52,
        "diameter_km": 6779,
        "moons": 2,
        "day_hours": 24.6,
        "year_days": 687,
        "fact": "Mars has the largest volcano in the solar system — Olympus Mons is three times the height of Everest and the size of Arizona.",
        "visibility": "Recognizable by its red-orange color. Brightness varies enormously depending on where it is in its orbit."
    },
    "Jupiter": {
        "type": "Gas Giant",
        "distance_au": 5.20,
        "diameter_km": 139820,
        "moons": 95,
        "day_hours": 9.9,
        "year_days": 4333,
        "fact": "Jupiter's Great Red Spot is a storm that has raged for at least 350 years. It's shrinking — in the 1800s it was three times Earth's diameter.",
        "visibility": "One of the brightest objects in the night sky. Even binoculars show its four largest moons — the Galilean moons."
    },
    "Saturn": {
        "type": "Gas Giant",
        "distance_au": 9.58,
        "diameter_km": 116460,
        "moons": 146,
        "day_hours": 10.7,
        "year_days": 10759,
        "fact": "Saturn is the least dense planet in the solar system — it would float in water. Its rings are made of ice and rock and are only about 30 feet thick despite being 170,000 miles wide.",
        "visibility": "Pale yellow color. Rings are visible in even a small telescope — one of the most stunning sights in amateur astronomy."
    },
    "Uranus": {
        "type": "Ice Giant",
        "distance_au": 19.2,
        "diameter_km": 50724,
        "moons": 27,
        "day_hours": 17.2,
        "year_days": 30687,
        "fact": "Uranus rotates on its side — its axial tilt is 98 degrees. It essentially rolls around the Sun like a bowling ball. Each pole gets 42 years of sunlight then 42 years of darkness.",
        "visibility": "Just barely visible to the naked eye under dark skies — appears as a faint blue-green dot. Binoculars or telescope needed to see it clearly."
    },
    "Neptune": {
        "type": "Ice Giant",
        "distance_au": 30.1,
        "diameter_km": 49244,
        "moons": 16,
        "day_hours": 16.1,
        "year_days": 60190,
        "fact": "Neptune has the fastest winds in the solar system — up to 1,200 mph. Its largest moon Triton orbits backwards and is slowly spiraling inward — in about 3.6 billion years it will be torn apart into rings.",
        "visibility": "Not visible to the naked eye. Requires a telescope. Appears as a tiny blue disk."
    },
}

def get_visible_constellations():
    """
    Return list of constellations visible tonight from Fringe Labs.
    Uses astroplan/astropy for real calculations.
    """
    try:
        from astroplan import Observer
        from astropy.coordinates import SkyCoord, AltAz, EarthLocation
        from astropy.time import Time
        import astropy.units as u

        location = EarthLocation(
            lat=FRINGE_LAT * u.deg,
            lon=FRINGE_LON * u.deg,
            height=FRINGE_ELEV * u.m
        )

        now = Time.now()
        # Check visibility at midnight local (approx)
        observe_time = now

        altaz_frame = AltAz(obstime=observe_time, location=location)

        visible = []
        for name, data in CONSTELLATIONS.items():
            coord = SkyCoord(ra=data['ra'] * u.hour, dec=data['dec'] * u.deg, frame='icrs')
            altaz = coord.transform_to(altaz_frame)
            alt = altaz.alt.deg
            if alt > 10:  # above 10 degrees elevation
                visible.append((name, round(alt, 1), round(altaz.az.deg, 1)))

        return sorted(visible, key=lambda x: x[1], reverse=True)

    except Exception as e:
        return []

def show_visible_tonight():
    """Display constellations visible right now from Fringe Labs."""
    console.print(f"\n[bold cyan]VISIBLE TONIGHT[/bold cyan]")
    console.print(f"[dim]{FRINGE_NAME}[/dim]")
    console.print(f"[dim]{datetime.now().strftime('%Y-%m-%d %H:%M')} local time[/dim]\n")

    visible = get_visible_constellations()

    if not visible:
        console.print("[yellow]Could not calculate visibility — check astroplan install.[/yellow]")
        return

    table = Table(box=box.SIMPLE, show_header=True, padding=(0, 2))
    table.add_column("Constellation", style="bold cyan", width=18)
    table.add_column("Altitude", style="white", width=10)
    table.add_column("Azimuth", style="white", width=10)
    table.add_column("Direction", style="green", width=12)

    def az_to_dir(az):
        dirs = ["N","NNE","NE","ENE","E","ESE","SE","SSE",
                "S","SSW","SW","WSW","W","WNW","NW","NNW"]
        idx = round(az / 22.5) % 16
        return dirs[idx]

    for name, alt, az in visible:
        table.add_row(name, f"{alt}°", f"{az}°", az_to_dir(az))

    console.print(Panel(
        table,
        title=f"[bold cyan]CONSTELLATIONS ABOVE HORIZON[/bold cyan]",
        subtitle=f"[dim]{len(visible)} visible[/dim]",
        border_style="cyan",
        padding=(1, 2)
    ))

def explore_constellation():
    """Let user pick a constellation and get full info."""
    console.print(f"\n[bold cyan]CONSTELLATION EXPLORER[/bold cyan]\n")

    names = sorted(CONSTELLATIONS.keys())
    for i, name in enumerate(names, 1):
        console.print(f"  [cyan]{i:2}[/cyan]  {name}")

    console.print()
    choice = input("  Select number (or type name): ").strip()

    # Handle number or name input
    selected = None
    if choice.isdigit():
        idx = int(choice) - 1
        if 0 <= idx < len(names):
            selected = names[idx]
    else:
        # Try name match
        for name in names:
            if name.lower() == choice.lower():
                selected = name
                break

    if not selected:
        console.print("[red]Invalid selection.[/red]")
        return

    data = CONSTELLATIONS[selected]

    # Build info table
    table = Table(box=box.SIMPLE, show_header=False, padding=(0, 2))
    table.add_column("Field", style="bold cyan", width=18)
    table.add_column("Value", style="white")

    table.add_row("Constellation", selected)
    table.add_row("Main stars", ", ".join(data['stars']))
    table.add_row("Best viewing", datetime(2000, data['best_month'], 1).strftime("%B"))
    table.add_row("RA center", f"{data['ra']}h")
    table.add_row("Dec center", f"{data['dec']}°")
    table.add_row("", "")
    table.add_row("Mythology", data['myth'])
    table.add_row("", "")
    table.add_row("Observer notes", data['notes'])

    console.print(Panel(
        table,
        title=f"[bold cyan]{selected.upper()}[/bold cyan]",
        border_style="cyan",
        padding=(1, 2)
    ))

def explore_planet():
    """Let user pick a planet and get full info."""
    console.print(f"\n[bold cyan]PLANET GUIDE[/bold cyan]\n")

    names = list(PLANETS.keys())
    for i, name in enumerate(names, 1):
        console.print(f"  [cyan]{i}[/cyan]  {name}")

    console.print()
    choice = input("  Select number (or type name): ").strip()

    selected = None
    if choice.isdigit():
        idx = int(choice) - 1
        if 0 <= idx < len(names):
            selected = names[idx]
    else:
        for name in names:
            if name.lower() == choice.lower():
                selected = name
                break

    if not selected:
        console.print("[red]Invalid selection.[/red]")
        return

    data = PLANETS[selected]

    table = Table(box=box.SIMPLE, show_header=False, padding=(0, 2))
    table.add_column("Field", style="bold cyan", width=20)
    table.add_column("Value", style="white")

    table.add_row("Planet", selected)
    table.add_row("Type", data['type'])
    table.add_row("Distance from Sun", f"{data['distance_au']} AU")
    table.add_row("Diameter", f"{data['diameter_km']:,} km")
    table.add_row("Moons", str(data['moons']))
    table.add_row("Day length", f"{data['day_hours']} hours")
    table.add_row("Year length", f"{data['year_days']} Earth days")
    table.add_row("", "")
    table.add_row("Visibility", data['visibility'])
    table.add_row("", "")
    table.add_row("Cool fact", data['fact'])

    console.print(Panel(
        table,
        title=f"[bold cyan]{selected.upper()}[/bold cyan]",
        border_style="cyan",
        padding=(1, 2)
    ))

def sky_menu():
    """Main sky guide menu."""
    while True:
        try:
            table = Table(box=box.SIMPLE, show_header=False, padding=(0, 2))
            table.add_column("Key", style="bold cyan", width=4)
            table.add_column("Option", style="white")

            table.add_row("1", "What's visible tonight")
            table.add_row("2", "Explore a constellation")
            table.add_row("3", "Planet guide")
            table.add_row("4", "Back")

            console.print(Panel(
                table,
                title="[bold cyan]FRINGE SKY GUIDE[/bold cyan]",
                subtitle=f"[dim]{FRINGE_NAME}[/dim]",
                border_style="cyan",
                padding=(1, 2)
            ))

            choice = input("  Select option: ").strip()

            if choice == "1":
                show_visible_tonight()
            elif choice == "2":
                explore_constellation()
            elif choice == "3":
                explore_planet()
            elif choice == "4":
                break
            else:
                console.print("[red]Invalid option.[/red]")

            input("\n  [Enter to continue]")

        except KeyboardInterrupt:
            break