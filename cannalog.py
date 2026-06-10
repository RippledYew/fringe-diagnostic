#!/usr/bin/env python3
"""
cannalog — Daily Flower Journal
Medical patient edition. CLI for quick entry, TUI for catalog browsing.
Storage: ~/.local/share/cannalog/entries.jsonl
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

# ── Storage ───────────────────────────────────────────────────────────────────

DATA_DIR  = Path.home() / ".local" / "share" / "cannalog"
DATA_FILE = DATA_DIR / "entries.jsonl"

def ensure_data_dir():
    DATA_DIR.mkdir(parents=True, exist_ok=True)

def load_entries():
    ensure_data_dir()
    if not DATA_FILE.exists():
        return []
    entries = []
    with open(DATA_FILE, "r") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    return entries

def save_entry(entry: dict):
    ensure_data_dir()
    with open(DATA_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")

def rewrite_entries(entries: list):
    """Overwrite the whole file — used for fav toggles and deletes."""
    ensure_data_dir()
    with open(DATA_FILE, "w") as f:
        for e in entries:
            f.write(json.dumps(e) + "\n")

# ── Rich setup ────────────────────────────────────────────────────────────────

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.prompt import Prompt, Confirm
    from rich.text import Text
    from rich.columns import Columns
    from rich import box
    from rich.align import Align
except ImportError:
    print("Rich is required: pip install rich")
    sys.exit(1)

console = Console()

# ── Palette helpers ───────────────────────────────────────────────────────────

TYPE_COLOR = {
    "indica":  "medium_purple1",
    "sativa":  "gold1",
    "hybrid":  "spring_green3",
}

def type_badge(t: str) -> Text:
    color = TYPE_COLOR.get(t, "white")
    return Text(f" {t.upper()} ", style=f"bold {color}")

def leaf_rating(n: int) -> str:
    if not n:
        return "[dim]unrated[/dim]"
    return "[green]🍃[/green]" * n + "[dim]🍃[/dim]" * (5 - n)

def fav_icon(e: dict) -> str:
    return "⭐" if e.get("fav") else "  "

def fmt_date(dt_str: str) -> str:
    try:
        dt = datetime.fromisoformat(dt_str)
        return dt.strftime("%b %d, %Y  %I:%M %p")
    except Exception:
        return dt_str or ""

# ── Banner ────────────────────────────────────────────────────────────────────

def print_banner():
    title = Text()
    title.append("🌿  Canna", style="bold yellow")
    title.append("-Log", style="italic white")
    subtitle = Text("Daily Flower Journal  ·  Medical Patient Edition",
                    style="dim green", justify="center")
    console.print(Panel(
        Align.center(title + Text("\n") + subtitle),
        border_style="dark_green",
        padding=(0, 4),
    ))

# ── CLI: add entry ────────────────────────────────────────────────────────────

def cmd_add(args):
    print_banner()
    console.print("\n[bold green]New Entry[/bold green]\n")

    # Strain
    strain = args.strain or Prompt.ask("[bold yellow]Strain name[/bold yellow]")
    if not strain.strip():
        console.print("[red]Strain name required.[/red]")
        sys.exit(1)

    # Type
    valid_types = ["indica", "sativa", "hybrid"]
    if args.type and args.type.lower() in valid_types:
        strain_type = args.type.lower()
    else:
        console.print("[dim]Types:[/dim]  [medium_purple1]indica[/medium_purple1]  "
                      "[gold1]sativa[/gold1]  [spring_green3]hybrid[/spring_green3]")
        while True:
            strain_type = Prompt.ask("[bold yellow]Type[/bold yellow]",
                                     default="hybrid").lower()
            if strain_type in valid_types:
                break
            console.print("[red]Enter indica, sativa, or hybrid.[/red]")

    # Dispensary
    dispensary = args.dispensary or Prompt.ask(
        "[bold yellow]Dispensary[/bold yellow]", default="")

    # Rating
    rating = 0
    if args.rating:
        try:
            r = int(args.rating)
            if 1 <= r <= 5:
                rating = r
        except ValueError:
            pass
    if not rating:
        console.print("[dim]Rate 1–5 leaves (0 to skip)[/dim]")
        while True:
            raw = Prompt.ask("[bold yellow]Rating[/bold yellow]  🍃 (1-5)", default="0")
            try:
                r = int(raw)
                if 0 <= r <= 5:
                    rating = r
                    break
            except ValueError:
                pass
            console.print("[red]Enter a number 0–5.[/red]")

    # Effects
    effects = args.effects or Prompt.ask(
        "[bold yellow]Effects notes[/bold yellow]", default="")

    # Flavor
    flavor = args.flavor or Prompt.ask(
        "[bold yellow]Flavor & aroma[/bold yellow]", default="")

    entry = {
        "id":         int(datetime.now().timestamp() * 1000),
        "strain":     strain.strip(),
        "type":       strain_type,
        "dispensary": dispensary.strip(),
        "datetime":   datetime.now().isoformat(timespec="minutes"),
        "rating":     rating,
        "effects":    effects.strip(),
        "flavor":     flavor.strip(),
        "fav":        False,
    }

    save_entry(entry)

    # Confirmation card
    console.print()
    _render_card(entry, index=None)
    console.print("\n[bold green]✓ Logged.[/bold green]\n")


# ── Card renderer (shared by TUI and CLI) ────────────────────────────────────

def _render_card(e: dict, index=None):
    fav     = "⭐ " if e.get("fav") else ""
    rating  = leaf_rating(e.get("rating", 0))
    tcolor  = TYPE_COLOR.get(e.get("type",""), "white")
    badge   = f"[bold {tcolor}]{e.get('type','').upper()}[/bold {tcolor}]"
    disp    = f"  [dim]📍 {e['dispensary']}[/dim]" if e.get("dispensary") else ""
    header  = f"{fav}[bold yellow]{e['strain']}[/bold yellow]  {badge}{disp}"

    body_lines = []
    body_lines.append(f"[dim]{fmt_date(e.get('datetime',''))}[/dim]   {rating}")
    if e.get("effects"):
        body_lines.append(f"\n[dim]Effects:[/dim]  {e['effects']}")
    if e.get("flavor"):
        body_lines.append(f"[dim]Flavor: [/dim]  {e['flavor']}")

    idx_label = f" #{index} " if index is not None else ""
    console.print(Panel(
        "\n".join(body_lines),
        title=header,
        title_align="left",
        subtitle=idx_label,
        subtitle_align="right",
        border_style="dark_green",
        padding=(0, 2),
    ))


# ── TUI: catalog browser ──────────────────────────────────────────────────────

def cmd_catalog(args):
    """Interactive catalog browser."""
    print_banner()

    filter_type = "all"
    filter_fav  = False
    search_term = ""

    while True:
        entries = load_entries()
        entries.sort(key=lambda e: e.get("datetime", ""), reverse=True)

        # Apply filters
        view = entries
        if filter_fav:
            view = [e for e in view if e.get("fav")]
        if filter_type != "all":
            view = [e for e in view if e.get("type") == filter_type]
        if search_term:
            q = search_term.lower()
            view = [e for e in view if q in (
                e.get("strain","") + e.get("dispensary","") +
                e.get("effects","") + e.get("flavor","")
            ).lower()]

        console.clear()
        print_banner()
        _render_stats(entries)
        _render_filter_bar(filter_type, filter_fav, search_term)

        if not view:
            console.print(Panel(
                Align.center("[dim]No entries match. Try a different filter.[/dim]"),
                border_style="dark_green", padding=(1,4)
            ))
        else:
            for i, e in enumerate(view):
                _render_card(e, index=i+1)

        # Command menu
        console.print(
            "\n[dim]Commands:[/dim]  "
            "[bold]a[/bold]=add  "
            "[bold]f[/bold]=toggle favs  "
            "[bold]t[/bold]=type filter  "
            "[bold]s[/bold]=search  "
            "[bold]★ N[/bold]=fav entry  "
            "[bold]d N[/bold]=delete  "
            "[bold]q[/bold]=quit"
        )

        cmd = Prompt.ask("\n[green]>[/green]", default="").strip().lower()

        if cmd == "q":
            console.print("\n[dim]Stay lifted. 🌿[/dim]\n")
            break

        elif cmd == "a":
            console.clear()
            # Drop into add flow without args
            _interactive_add()

        elif cmd == "f":
            filter_fav = not filter_fav

        elif cmd == "t":
            opts = "[medium_purple1]indica[/medium_purple1]  " \
                   "[gold1]sativa[/gold1]  " \
                   "[spring_green3]hybrid[/spring_green3]  " \
                   "[white]all[/white]"
            console.print(f"Filter by type: {opts}")
            t = Prompt.ask("Type", default="all").lower()
            filter_type = t if t in ["indica","sativa","hybrid","all"] else "all"

        elif cmd == "s":
            search_term = Prompt.ask("Search", default="")

        elif cmd.startswith("★") or cmd.startswith("*"):
            # fav toggle: "* 3" or "★3"
            parts = cmd.replace("★","").replace("*","").strip().split()
            if parts and parts[0].isdigit():
                idx = int(parts[0]) - 1
                if 0 <= idx < len(view):
                    target_id = view[idx]["id"]
                    all_e = load_entries()
                    for e in all_e:
                        if e["id"] == target_id:
                            e["fav"] = not e.get("fav", False)
                    rewrite_entries(all_e)

        elif cmd.startswith("d"):
            parts = cmd.split()
            if len(parts) == 2 and parts[1].isdigit():
                idx = int(parts[1]) - 1
                if 0 <= idx < len(view):
                    target = view[idx]
                    console.print(f"Delete [bold]{target['strain']}[/bold]?", end=" ")
                    if Confirm.ask(""):
                        rewrite_entries([e for e in load_entries()
                                         if e["id"] != target["id"]])


def _render_stats(entries):
    rated   = [e for e in entries if e.get("rating")]
    avg     = f"{sum(e['rating'] for e in rated)/len(rated):.1f}" if rated else "—"
    fav_ct  = sum(1 for e in entries if e.get("fav"))
    top     = max(entries, key=lambda e: e.get("rating",0)).get("strain","—") if entries else "—"

    t = Table(box=None, padding=(0,3,0,0), show_header=False)
    t.add_column(style="dim green")
    t.add_column(style="bold yellow")
    t.add_row("Logged",    str(len(entries)))
    t.add_row("Avg rating", avg)
    t.add_row("Favorites",  str(fav_ct))
    t.add_row("Top rated",  top)
    t.add_row("Indica",    str(sum(1 for e in entries if e.get("type")=="indica")))
    t.add_row("Sativa",    str(sum(1 for e in entries if e.get("type")=="sativa")))
    t.add_row("Hybrid",    str(sum(1 for e in entries if e.get("type")=="hybrid")))

    console.print(Panel(t, title="[dim]Stats[/dim]", border_style="dark_green",
                        padding=(0,2), expand=False))


def _render_filter_bar(filter_type, filter_fav, search_term):
    parts = []
    parts.append(f"[dim]Type:[/dim] [bold yellow]{filter_type}[/bold yellow]")
    parts.append(f"[dim]Favs only:[/dim] [bold yellow]{'yes' if filter_fav else 'no'}[/bold yellow]")
    if search_term:
        parts.append(f"[dim]Search:[/dim] [bold yellow]\"{search_term}\"[/bold yellow]")
    console.print("  " + "   ·   ".join(parts) + "\n")


def _interactive_add():
    """Add flow called from within the TUI (no argparse)."""
    console.print(Panel("[bold green]New Entry[/bold green]", border_style="dark_green"))

    strain = Prompt.ask("[bold yellow]Strain name[/bold yellow]")
    if not strain.strip():
        console.print("[red]Cancelled — no strain name.[/red]")
        return

    console.print("[dim]indica / sativa / hybrid[/dim]")
    while True:
        strain_type = Prompt.ask("[bold yellow]Type[/bold yellow]", default="hybrid").lower()
        if strain_type in ["indica","sativa","hybrid"]:
            break
        console.print("[red]Enter indica, sativa, or hybrid.[/red]")

    dispensary = Prompt.ask("[bold yellow]Dispensary[/bold yellow]", default="")

    while True:
        raw = Prompt.ask("[bold yellow]Rating[/bold yellow]  🍃 (1-5, 0=skip)", default="0")
        try:
            r = int(raw)
            if 0 <= r <= 5:
                rating = r
                break
        except ValueError:
            pass

    effects = Prompt.ask("[bold yellow]Effects notes[/bold yellow]", default="")
    flavor  = Prompt.ask("[bold yellow]Flavor & aroma[/bold yellow]", default="")

    entry = {
        "id":         int(datetime.now().timestamp() * 1000),
        "strain":     strain.strip(),
        "type":       strain_type,
        "dispensary": dispensary.strip(),
        "datetime":   datetime.now().isoformat(timespec="minutes"),
        "rating":     rating,
        "effects":    effects.strip(),
        "flavor":     flavor.strip(),
        "fav":        False,
    }
    save_entry(entry)
    console.print("\n[bold green]✓ Logged.[/bold green]")
    _render_card(entry)


# ── CLI: quick stats ──────────────────────────────────────────────────────────

def cmd_stats(args):
    print_banner()
    entries = load_entries()
    if not entries:
        console.print("[dim]No entries yet. Run: cannalog add[/dim]")
        return
    _render_stats(entries)


# ── CLI: toggle favorite by strain name ──────────────────────────────────────

def cmd_fav(args):
    entries = load_entries()
    name = " ".join(args.strain).lower()
    matched = [e for e in entries if e["strain"].lower() == name]
    if not matched:
        # fuzzy: partial match
        matched = [e for e in entries if name in e["strain"].lower()]
    if not matched:
        console.print(f"[red]No entry found matching '{name}'[/red]")
        sys.exit(1)
    target = matched[0]
    target["fav"] = not target.get("fav", False)
    rewrite_entries(entries)
    icon = "⭐" if target["fav"] else "  "
    console.print(f"{icon} [bold yellow]{target['strain']}[/bold yellow] "
                  f"{'marked as favorite' if target['fav'] else 'removed from favorites'}")


# ── Entry point ───────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        prog="cannalog",
        description="🌿 Daily Flower Journal — Medical Patient Edition",
    )
    sub = parser.add_subparsers(dest="command")

    # add
    p_add = sub.add_parser("add", help="Log a new sample (interactive or with flags)")
    p_add.add_argument("strain",      nargs="?",  help="Strain name")
    p_add.add_argument("-t", "--type",             help="indica / sativa / hybrid")
    p_add.add_argument("-d", "--dispensary",        help="Dispensary name")
    p_add.add_argument("-r", "--rating",            help="Rating 1–5")
    p_add.add_argument("-e", "--effects",           help="Effects notes")
    p_add.add_argument("-f", "--flavor",            help="Flavor & aroma notes")

    # catalog
    sub.add_parser("catalog", help="Browse catalog (interactive TUI)")

    # stats
    sub.add_parser("stats", help="Quick stats summary")

    # fav
    p_fav = sub.add_parser("fav", help="Toggle favorite on a strain")
    p_fav.add_argument("strain", nargs="+", help="Strain name (partial match ok)")

    args = parser.parse_args()

    if args.command == "add":
        cmd_add(args)
    elif args.command == "catalog":
        cmd_catalog(args)
    elif args.command == "stats":
        cmd_stats(args)
    elif args.command == "fav":
        cmd_fav(args)
    else:
        # No subcommand — drop straight into catalog if entries exist, else add
        entries = load_entries()
        if entries:
            cmd_catalog(args)
        else:
            console.print("[dim]No entries yet.[/dim]")
            console.print("Run [bold green]cannalog add[/bold green] to log your first sample.\n")


if __name__ == "__main__":
    main()
