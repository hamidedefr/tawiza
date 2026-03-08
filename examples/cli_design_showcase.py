#!/usr/bin/env python3
"""
CLI Design Showcase - MPtoO-V2
Démonstration complète de tous les composants et fonctionnalités UI
"""

import time

import questionary
from rich import box
from rich.align import Align
from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.table import Table

console = Console()


# ==== DEMO 1: THÈMES ====
def demo_themes():
    console.clear()
    console.print("\n[bold cyan]🎨 THÈMES MULTIPLES[/bold cyan]\n")

    themes = {
        "Sunset 🌅": {"primary": "#FF6B35", "desc": "Chaleureux et accueillant"},
        "Ocean 🌊": {"primary": "#1E90FF", "desc": "Apaisant et professionnel"},
        "Forest 🌲": {"primary": "#228B22", "desc": "Naturel et zen"},
        "Neon ⚡": {"primary": "#FF00FF", "desc": "Énergique et moderne"},
        "Midnight 🌙": {"primary": "#9370DB", "desc": "Élégant et subtil"},
    }

    for name, data in themes.items():
        panel = Panel(
            f"[{data['primary']}]████████████████████[/]\n[dim]{data['desc']}[/]",
            title=f"[bold {data['primary']}]{name}[/]",
            border_style=data["primary"],
            box=box.ROUNDED,
        )
        console.print(panel)

    console.input("\n[dim]Entrée pour continuer...[/dim]")


# ==== DEMO 2: STATUS BOXES ====
def demo_status():
    console.clear()
    console.print("\n[bold cyan]📦 COMPOSANTS STATUS[/bold cyan]\n")

    console.print(
        Panel("[bold green]✅ Training completed![/]", border_style="green", box=box.ROUNDED)
    )
    console.print(Panel("[bold red]❌ GPU not found[/]", border_style="red", box=box.ROUNDED))
    console.print(
        Panel("[bold yellow]⚠️  High memory usage[/]", border_style="yellow", box=box.ROUNDED)
    )
    console.print(Panel("[bold cyan]ℹ️  Update available[/]", border_style="cyan", box=box.ROUNDED))

    console.input("\n[dim]Entrée pour continuer...[/dim]")


# ==== DEMO 3: MÉTRIQUES ====
def demo_metrics():
    console.clear()
    console.print("\n[bold cyan]📊 MÉTRIQUES[/bold cyan]\n")

    table = Table(title="System Metrics", box=box.ROUNDED, show_header=False)
    table.add_column(style="cyan", width=20)
    table.add_column(style="white")

    table.add_row("CPU Usage:", "[yellow]75.3%[/] ↑")
    table.add_row("RAM Usage:", "[green]4.2 GB[/] →")
    table.add_row("GPU Usage:", "[yellow]82.1%[/] ↑")
    table.add_row("Tasks:", "[cyan]156[/] ↑")

    console.print(table)
    console.input("\n[dim]Entrée pour continuer...[/dim]")


# ==== DEMO 4: PROGRESS ====
def demo_progress():
    console.clear()
    console.print("\n[bold cyan]⏳ PROGRESS BARS[/bold cyan]\n")

    console.print("[bold]Training Progress:[/]")
    bar = "█" * 26 + "░" * 14
    console.print(f"[cyan]{bar}[/] 65%\n")

    console.print("[bold]Multi-Step:[/]\n")
    steps = [
        ("Data Loading", 100, "green", "✅"),
        ("Training", 65, "cyan", "🔄"),
        ("Validation", 0, "dim white", "⏸️"),
    ]

    for name, pct, color, icon in steps:
        bar = "█" * int(30 * pct / 100) + "░" * (30 - int(30 * pct / 100))
        console.print(f"{icon} {name:15} [{color}]{bar}[/] {pct}%")

    console.input("\n[dim]Entrée pour continuer...[/dim]")


# ==== DEMO 5: TABLEAUX ====
def demo_tables():
    console.clear()
    console.print("\n[bold cyan]📋 TABLEAUX AVANCÉS[/bold cyan]\n")

    table = Table(title="Agent Status", box=box.ROUNDED)
    table.add_column("Agent", style="cyan")
    table.add_column("Status")
    table.add_column("Tasks", justify="right")

    table.add_row("ML Engineer", "[green]✅ Running[/]", "42")
    table.add_row("Data Analyst", "[green]✅ Running[/]", "38")
    table.add_row("Optimizer", "[yellow]💤 Idle[/]", "0")

    console.print(table)
    console.input("\n[dim]Entrée pour continuer...[/dim]")


# ==== DEMO 6: GRAPHIQUES ====
def demo_charts():
    console.clear()
    console.print("\n[bold cyan]📈 GRAPHIQUES ASCII[/bold cyan]\n")

    console.print("[bold]Sparklines:[/]\n")
    console.print("[cyan]CPU    [/] [green]▁▂▃▄▅▆▇█▇▆▅▄▃▂▁[/]")
    console.print("[cyan]Memory [/] [green]▃▃▄▄▅▅▆▆▇▇██▇▇[/]\n")

    console.print("[bold]Bar Chart:[/]\n")
    data = {"ML Engineer": 42, "Data Analyst": 38, "Optimizer": 15}
    for name, value in data.items():
        bar = "█" * int(30 * value / 42)
        console.print(f"[cyan]{name:15}[/] [green]{bar}[/] {value}")

    console.input("\n[dim]Entrée pour continuer...[/dim]")


# ==== DEMO 7: ANIMATIONS ====
def demo_animations():
    console.clear()
    console.print("\n[bold cyan]✨ ANIMATIONS[/bold cyan]\n")

    console.print("[bold]Spinners:[/]\n")
    frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧"]
    console.print("[cyan]Loading [/] ", end="")
    for frame in frames * 3:
        console.print(f"[green]{frame}[/]", end="", flush=True)
        time.sleep(0.1)
        console.print("\b \b", end="")
    console.print("[green]✓[/]")

    console.input("\n[dim]Entrée pour continuer...[/dim]")


# ==== DEMO 8: INTERACTIF ====
def demo_interactive():
    console.clear()
    console.print("\n[bold cyan]🖱️  INTERACTIF[/bold cyan]\n")

    choice = questionary.select(
        "Sélectionnez un thème:", choices=["🌅 Sunset", "🌊 Ocean", "🌲 Forest", "⚡ Neon"]
    ).ask()

    console.print(f"\n[green]✓ {choice} sélectionné![/]")
    console.input("\n[dim]Entrée pour continuer...[/dim]")


# ==== DEMO 9: DASHBOARD LIVE ====
def demo_live():
    console.clear()
    console.print("\n[bold cyan]📊 DASHBOARD LIVE[/bold cyan]\n")
    console.print("[dim]Updating for 5 seconds...[/dim]\n")
    time.sleep(1)

    def gen_dashboard(i):
        table = Table(show_header=False, box=box.SIMPLE)
        table.add_column(style="cyan")
        table.add_column(style="white")

        table.add_row("CPU", f"[yellow]{60 + i % 20}%[/]")
        table.add_row("Tasks", f"[cyan]{150 + i}[/]")

        return Panel(table, title="Live Stats", border_style="cyan")

    with Live(gen_dashboard(0), console=console, refresh_per_second=2) as live:
        for i in range(10):
            time.sleep(0.5)
            live.update(gen_dashboard(i))

    console.print("\n[green]✓ Live demo complete![/]")
    console.input("\n[dim]Entrée pour terminer...[/dim]")


# ==== MAIN ====
def main():
    console.clear()
    console.print(
        Panel(
            Align.center("[bold cyan]CLI Design Showcase[/]\n[dim]MPtoO-V2[/]"),
            border_style="cyan",
            box=box.DOUBLE,
        )
    )

    demos = [
        ("Thèmes", demo_themes),
        ("Status", demo_status),
        ("Métriques", demo_metrics),
        ("Progress", demo_progress),
        ("Tableaux", demo_tables),
        ("Graphiques", demo_charts),
        ("Animations", demo_animations),
        ("Interactif", demo_interactive),
        ("Dashboard Live", demo_live),
    ]

    for i, (name, func) in enumerate(demos, 1):
        console.print(f"\n[cyan]{i}/{len(demos)}[/] [bold]{name}[/]")
        func()

    console.clear()
    console.print(
        Panel(
            Align.center("[bold green]🎉 Showcase Complete![/]"),
            border_style="green",
            box=box.DOUBLE,
        )
    )


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted[/]")
