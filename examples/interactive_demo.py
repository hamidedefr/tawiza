#!/usr/bin/env python3
"""
Demo Interactive Components - Phase 2
Démonstration complète des composants interactifs et wizards
"""

from rich import box
from rich.console import Console
from rich.panel import Panel

from src.cli.ui.interactive import FilePicker, InteractiveMenu, InteractivePrompt
from src.cli.ui.wizards import (
    agent_configuration_wizard,
    model_selection_wizard,
    performance_tuning_wizard,
    setup_wizard,
)

console = Console()


def main_menu():
    """Menu principal de la démo"""
    while True:
        console.clear()
        console.print(
            Panel(
                "[bold cyan]Interactive Components Demo - Phase 2[/]\n"
                "[dim]Menus, Prompts, Forms & Wizards[/]",
                border_style="cyan",
                box=box.DOUBLE,
            )
        )
        console.print()

        choice = InteractiveMenu.select(
            "What would you like to demo?",
            choices=[
                "1️⃣  Simple Select Menu",
                "2️⃣  Multi-Select Menu",
                "3️⃣  Text Prompts with Validation",
                "4️⃣  Number Prompts",
                "5️⃣  File Picker",
                "6️⃣  🚀 Setup Wizard",
                "7️⃣  🤖 Agent Configuration Wizard",
                "8️⃣  🎯 Model Selection Wizard",
                "9️⃣  ⚡ Performance Tuning Wizard",
                "❌ Exit",
            ],
        )

        if choice == "❌ Exit":
            console.print("\n[yellow]Goodbye![/]")
            break

        elif choice == "1️⃣  Simple Select Menu":
            demo_simple_select()

        elif choice == "2️⃣  Multi-Select Menu":
            demo_multi_select()

        elif choice == "3️⃣  Text Prompts with Validation":
            demo_text_prompts()

        elif choice == "4️⃣  Number Prompts":
            demo_number_prompts()

        elif choice == "5️⃣  File Picker":
            demo_file_picker()

        elif choice == "6️⃣  🚀 Setup Wizard":
            results = setup_wizard()
            if results:
                console.print("\n[green]✓ Setup complete![/]")
                console.input("\nPress Enter to continue...")

        elif choice == "7️⃣  🤖 Agent Configuration Wizard":
            results = agent_configuration_wizard()
            if results:
                console.print("\n[green]✓ Agent configured![/]")
                console.input("\nPress Enter to continue...")

        elif choice == "8️⃣  🎯 Model Selection Wizard":
            results = model_selection_wizard()
            if results:
                console.print("\n[green]✓ Model selected![/]")
                console.input("\nPress Enter to continue...")

        elif choice == "9️⃣  ⚡ Performance Tuning Wizard":
            results = performance_tuning_wizard()
            if results:
                console.print("\n[green]✓ Performance tuned![/]")
                console.input("\nPress Enter to continue...")


def demo_simple_select():
    """Demo: Simple select menu"""
    console.clear()
    console.print("[bold cyan]Simple Select Menu Demo[/]\n")

    theme = InteractiveMenu.select(
        "Choose your favorite theme:",
        choices=[
            "🌅 Sunset - Warm and welcoming",
            "🌊 Ocean - Calm and professional",
            "🌲 Forest - Natural and zen",
            "⚡ Neon - Energetic and modern",
            "🌙 Midnight - Elegant and subtle",
        ],
        instruction="Use arrow keys to navigate",
    )

    console.print(f"\n[green]✓ You selected: {theme}[/]")
    console.input("\nPress Enter to continue...")


def demo_multi_select():
    """Demo: Multi-select menu"""
    console.clear()
    console.print("[bold cyan]Multi-Select Menu Demo[/]\n")

    features = InteractiveMenu.multi_select(
        "Select features to enable:",
        choices=[
            "Smart Cache - Predictive caching",
            "Auto-retry - Automatic retry on failure",
            "Monitoring - Real-time monitoring",
            "Logging - Detailed logging",
            "Benchmarking - Performance benchmarks",
            "GPU Optimization - GPU acceleration",
        ],
        instruction="Space to select, Enter to confirm",
    )

    console.print(f"\n[green]✓ You selected {len(features)} features:[/]")
    for feature in features:
        console.print(f"  • {feature}")

    console.input("\nPress Enter to continue...")


def demo_text_prompts():
    """Demo: Text prompts with validation"""
    console.clear()
    console.print("[bold cyan]Text Prompts with Validation Demo[/]\n")

    from src.cli.ui.interactive import ValidationRule

    # Name with validation
    name = InteractivePrompt.text(
        "Enter your name:",
        validate=ValidationRule(
            validator=lambda x: len(x) >= 3, error_message="Name must be at least 3 characters"
        ),
    )

    # Email with validation
    email = InteractivePrompt.text(
        "Enter your email:",
        validate=ValidationRule(
            validator=lambda x: "@" in x and "." in x,
            error_message="Please enter a valid email address",
        ),
    )

    console.print(f"\n[green]✓ Name: {name}[/]")
    console.print(f"[green]✓ Email: {email}[/]")

    console.input("\nPress Enter to continue...")


def demo_number_prompts():
    """Demo: Number prompts"""
    console.clear()
    console.print("[bold cyan]Number Prompts Demo[/]\n")

    workers = InteractivePrompt.integer(
        "Number of parallel workers:", default=4, min_value=1, max_value=16
    )

    cache_size = InteractivePrompt.integer(
        "Cache size (max entries):", default=1000, min_value=100, max_value=10000
    )

    timeout = InteractivePrompt.number(
        "Timeout (seconds):", default=300.0, min_value=10.0, max_value=3600.0
    )

    console.print(f"\n[green]✓ Workers: {workers}[/]")
    console.print(f"[green]✓ Cache size: {cache_size}[/]")
    console.print(f"[green]✓ Timeout: {timeout}s[/]")

    console.input("\nPress Enter to continue...")


def demo_file_picker():
    """Demo: File picker"""
    console.clear()
    console.print("[bold cyan]File Picker Demo[/]\n")

    from pathlib import Path

    console.print("Select a Python file in the current directory:\n")

    selected_file = FilePicker.select_file(
        question="Choose a file:", directory=Path.cwd(), pattern="*.py"
    )

    if selected_file:
        console.print(f"\n[green]✓ Selected file: {selected_file}[/]")
    else:
        console.print("\n[yellow]No file selected[/]")

    console.input("\nPress Enter to continue...")


if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        console.print("\n\n[yellow]Demo interrupted by user[/]")
    except Exception as e:
        console.print(f"\n\n[red]Error: {e}[/]")
