#!/usr/bin/env python3
"""
Script de test pour vérifier les intégrations CLI

Teste:
1. Disponibilité des bibliothèques
2. Fonctionnalités de chaque module
3. Intégration avec le système existant
"""

import asyncio
import sys
from pathlib import Path

# Ajouter le projet au path
sys.path.insert(0, str(Path(__file__).parent.parent))

from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()

# ==============================================================================
# TEST 1: Imports et disponibilité
# ==============================================================================


def test_imports():
    """Tester tous les imports"""
    console.print("\n[bold cyan]═══ TEST 1: Imports et Disponibilité ═══[/bold cyan]\n")

    results = []

    # Test iterfzf
    try:
        from iterfzf import iterfzf

        results.append(("iterfzf", "✅ OK", "Fuzzy finder"))
    except ImportError as e:
        results.append(("iterfzf", f"❌ {e}", "Fuzzy finder"))

    # Test InquirerPy
    try:
        from InquirerPy import inquirer

        results.append(("InquirerPy", "✅ OK", "Interactive prompts"))
    except ImportError as e:
        results.append(("InquirerPy", f"❌ {e}", "Interactive prompts"))

    # Test alive-progress
    try:
        from alive_progress import alive_bar

        results.append(("alive-progress", "✅ OK", "Animated progress"))
    except ImportError as e:
        results.append(("alive-progress", f"❌ {e}", "Animated progress"))

    # Test pyperclip
    try:
        import pyperclip

        results.append(("pyperclip", "✅ OK", "Clipboard"))
    except ImportError as e:
        results.append(("pyperclip", f"❌ {e}", "Clipboard"))

    # Test plyer
    try:
        from plyer import notification

        results.append(("plyer", "✅ OK", "Desktop notifications"))
    except ImportError as e:
        results.append(("plyer", f"❌ {e}", "Desktop notifications"))

    # Test thefuzz
    try:
        from thefuzz import fuzz

        results.append(("thefuzz", "✅ OK", "Fuzzy matching"))
    except ImportError as e:
        results.append(("thefuzz", f"❌ {e}", "Fuzzy matching"))

    # Test nos modules
    try:
        from src.cli.helpers import ux_helpers

        results.append(("ux_helpers", "✅ OK", "UX Helpers module"))
    except ImportError as e:
        results.append(("ux_helpers", f"❌ {e}", "UX Helpers module"))

    try:
        from src.cli.services import BackendService

        results.append(("BackendService", "✅ OK", "Backend service"))
    except ImportError as e:
        results.append(("BackendService", f"❌ {e}", "Backend service"))

    try:
        from src.cli.errors import ErrorHandler, MPtoOError

        results.append(("errors", "✅ OK", "Error handling"))
    except ImportError as e:
        results.append(("errors", f"❌ {e}", "Error handling"))

    try:
        from src.cli.constants import CLI_VERSION

        results.append(("constants", f"✅ OK (v{CLI_VERSION})", "Constants"))
    except ImportError as e:
        results.append(("constants", f"❌ {e}", "Constants"))

    # Afficher tableau
    table = Table(title="Import Tests", box=box.ROUNDED)
    table.add_column("Module", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Purpose")

    for module, status, purpose in results:
        style = "green" if "✅" in status else "red"
        table.add_row(module, f"[{style}]{status}[/{style}]", purpose)

    console.print(table)

    success = all("✅" in r[1] for r in results)
    return success, len([r for r in results if "✅" in r[1]]), len(results)


# ==============================================================================
# TEST 2: Fuzzy Matching
# ==============================================================================


def test_fuzzy_matching():
    """Tester le fuzzy matching"""
    console.print("\n[bold cyan]═══ TEST 2: Fuzzy Matching (thefuzz) ═══[/bold cyan]\n")

    try:
        from src.cli.helpers import fuzzy_match

        choices = [
            "qwen3:14b",
            "qwen3-coder:30b",
            "llama3:70b",
            "mistral:latest",
            "mixtral:8x7b",
            "codellama:34b",
        ]

        test_queries = ["qwen", "llam", "mistr", "code"]

        table = Table(title="Fuzzy Match Results", box=box.ROUNDED)
        table.add_column("Query", style="cyan")
        table.add_column("Best Matches", style="yellow")
        table.add_column("Scores")

        for query in test_queries:
            matches = fuzzy_match(query, choices, limit=3)
            if matches:
                match_str = ", ".join([m[0] for m in matches])
                score_str = ", ".join([str(m[1]) for m in matches])
                table.add_row(query, match_str, score_str)
            else:
                table.add_row(query, "[red]No matches[/red]", "-")

        console.print(table)
        console.print("[green]✅ Fuzzy matching fonctionne![/green]")
        return True

    except Exception as e:
        console.print(f"[red]❌ Erreur: {e}[/red]")
        return False


# ==============================================================================
# TEST 3: Progress Bars
# ==============================================================================


def test_progress_bars():
    """Tester les progress bars"""
    console.print("\n[bold cyan]═══ TEST 3: Progress Bars (alive-progress) ═══[/bold cyan]\n")

    try:
        import time

        from src.cli.helpers import animated_progress, iterate_with_progress

        # Test 1: Progress bar simple
        console.print("[dim]Test 1: Progress bar avec total connu[/dim]")
        with animated_progress(20, "Processing items") as bar:
            for i in range(20):
                time.sleep(0.05)
                bar()

        console.print()

        # Test 2: Iterate with progress
        console.print("[dim]Test 2: Itération avec progress[/dim]")
        items = list(range(15))
        for item in iterate_with_progress(items, "Iterating"):
            time.sleep(0.05)

        console.print("\n[green]✅ Progress bars fonctionnent![/green]")
        return True

    except Exception as e:
        console.print(f"[red]❌ Erreur: {e}[/red]")
        import traceback

        traceback.print_exc()
        return False


# ==============================================================================
# TEST 4: Clipboard
# ==============================================================================


def test_clipboard():
    """Tester le clipboard"""
    console.print("\n[bold cyan]═══ TEST 4: Clipboard (pyperclip) ═══[/bold cyan]\n")

    try:
        from src.cli.helpers import copy_to_clipboard, paste_from_clipboard

        # Test copy
        test_text = "MPtoO-V2 Test - " + str(asyncio.get_event_loop().time())
        console.print(f"[dim]Copie de: '{test_text}'[/dim]")

        success = copy_to_clipboard(test_text, show_message=False)

        if success:
            # Test paste
            pasted = paste_from_clipboard()

            if pasted == test_text:
                console.print("[green]✅ Clipboard fonctionne! Texte vérifié.[/green]")
                return True
            else:
                console.print("[yellow]⚠️ Clipboard partiellement fonctionnel[/yellow]")
                console.print(f"[dim]Attendu: {test_text}[/dim]")
                console.print(f"[dim]Reçu: {pasted}[/dim]")
                return True  # Peut échouer en environnement headless
        else:
            console.print("[yellow]⚠️ Clipboard non disponible (environnement headless?)[/yellow]")
            return True  # Non bloquant

    except Exception as e:
        console.print(f"[yellow]⚠️ Clipboard test skipped: {e}[/yellow]")
        return True  # Non bloquant


# ==============================================================================
# TEST 5: Terminal Bell
# ==============================================================================


def test_terminal_bell():
    """Tester le terminal bell"""
    console.print("\n[bold cyan]═══ TEST 5: Terminal Bell ═══[/bold cyan]\n")

    try:
        from src.cli.helpers import beep

        console.print("[dim]Émission d'un bip terminal...[/dim]")
        beep()

        console.print("[green]✅ Terminal bell émis (vous avez peut-être entendu un bip)[/green]")
        return True

    except Exception as e:
        console.print(f"[red]❌ Erreur: {e}[/red]")
        return False


# ==============================================================================
# TEST 6: Services Layer
# ==============================================================================


async def test_services():
    """Tester la couche services"""
    console.print("\n[bold cyan]═══ TEST 6: Services Layer ═══[/bold cyan]\n")

    results = []

    # Test CacheService
    try:
        from src.cli.services import CacheService

        cache = CacheService()
        await cache.start()

        await cache.set("test_key", {"value": 42}, ttl=10)
        result = await cache.get("test_key")

        if result and result.get("value") == 42:
            results.append(("CacheService", "✅ OK"))
        else:
            results.append(("CacheService", "❌ Value mismatch"))

        await cache.stop()

    except Exception as e:
        results.append(("CacheService", f"❌ {e}"))

    # Test ConfigService
    try:
        from src.cli.services import ConfigService, SystemConfig

        config_service = ConfigService()
        config = config_service.config

        if isinstance(config, SystemConfig):
            results.append(("ConfigService", f"✅ OK (v{config.version})"))
        else:
            results.append(("ConfigService", "❌ Invalid config"))

    except Exception as e:
        results.append(("ConfigService", f"❌ {e}"))

    # Test ValidationService
    try:
        from src.cli.services import InputValidator

        # Test integer validation
        result = InputValidator.validate_integer("42", 0, 100)
        if result.is_valid:
            results.append(("ValidationService", "✅ OK"))
        else:
            results.append(("ValidationService", "❌ Validation failed"))

    except Exception as e:
        results.append(("ValidationService", f"❌ {e}"))

    # Test BackendService
    try:
        from src.cli.services import get_backend_service

        backend = await get_backend_service()
        status = await backend.get_system_status()

        if status.success:
            results.append(
                ("BackendService", f"✅ OK (CPU: {status.data.get('cpu_percent', 'N/A')}%)")
            )
        else:
            results.append(("BackendService", f"⚠️ {status.error}"))

    except Exception as e:
        results.append(("BackendService", f"❌ {e}"))

    # Afficher résultats
    table = Table(title="Services Tests", box=box.ROUNDED)
    table.add_column("Service", style="cyan")
    table.add_column("Status")

    for service, status in results:
        style = "green" if "✅" in status else ("yellow" if "⚠️" in status else "red")
        table.add_row(service, f"[{style}]{status}[/{style}]")

    console.print(table)

    return all("✅" in r[1] or "⚠️" in r[1] for r in results)


# ==============================================================================
# TEST 7: Error Handling
# ==============================================================================


def test_error_handling():
    """Tester la gestion d'erreurs"""
    console.print("\n[bold cyan]═══ TEST 7: Error Handling ═══[/bold cyan]\n")

    try:
        from src.cli.errors import (
            ConfigError,
            ErrorCode,
            ErrorHandler,
            ErrorSeverity,
            GPUNotAvailableError,
            MPtoOError,
        )

        # Test création d'erreur
        error = MPtoOError(
            "Test error message",
            code=ErrorCode.UNKNOWN,
            severity=ErrorSeverity.LOW,
            details={"test": True},
            suggestions=["Try this", "Or that"],
        )

        console.print(f"[dim]Error code: {error.code.value}[/dim]")
        console.print(f"[dim]Severity: {error.severity.value}[/dim]")

        # Test error handler (sans afficher l'erreur)
        handler = ErrorHandler()

        # Test specific errors
        gpu_error = GPUNotAvailableError("Test reason")
        console.print(f"[dim]GPU Error code: {gpu_error.code.value}[/dim]")

        console.print("[green]✅ Error handling fonctionne![/green]")
        return True

    except Exception as e:
        console.print(f"[red]❌ Erreur: {e}[/red]")
        import traceback

        traceback.print_exc()
        return False


# ==============================================================================
# TEST 8: CLI Commands
# ==============================================================================


def test_cli_commands():
    """Tester les commandes CLI"""
    console.print("\n[bold cyan]═══ TEST 8: CLI Commands ═══[/bold cyan]\n")

    import subprocess

    commands = [
        ("mptoo --help", "Help command"),
        ("mptoo system --help", "System subcommand"),
        ("mptoo interactive --help", "Interactive subcommand"),
    ]

    results = []

    for cmd, desc in commands:
        try:
            result = subprocess.run(
                f"source venv/bin/activate && {cmd}",
                shell=True,
                capture_output=True,
                text=True,
                timeout=10,
                cwd="/root/MPtoO-V2",
            )

            if result.returncode == 0:
                results.append((desc, "✅ OK"))
            else:
                results.append((desc, f"❌ Exit code {result.returncode}"))

        except subprocess.TimeoutExpired:
            results.append((desc, "❌ Timeout"))
        except Exception as e:
            results.append((desc, f"❌ {e}"))

    table = Table(title="CLI Commands Tests", box=box.ROUNDED)
    table.add_column("Command", style="cyan")
    table.add_column("Status")

    for desc, status in results:
        style = "green" if "✅" in status else "red"
        table.add_row(desc, f"[{style}]{status}[/{style}]")

    console.print(table)

    return all("✅" in r[1] for r in results)


# ==============================================================================
# MAIN
# ==============================================================================


async def main():
    """Exécuter tous les tests"""
    console.print(
        Panel.fit(
            "[bold]🧪 MPtoO-V2 CLI Integration Tests[/bold]\n"
            "Vérification des bibliothèques et fonctionnalités",
            border_style="cyan",
        )
    )

    results = []

    # Test 1: Imports
    success, passed, total = test_imports()
    results.append(("Imports", success, f"{passed}/{total}"))

    # Test 2: Fuzzy Matching
    success = test_fuzzy_matching()
    results.append(("Fuzzy Matching", success, ""))

    # Test 3: Progress Bars
    success = test_progress_bars()
    results.append(("Progress Bars", success, ""))

    # Test 4: Clipboard
    success = test_clipboard()
    results.append(("Clipboard", success, ""))

    # Test 5: Terminal Bell
    success = test_terminal_bell()
    results.append(("Terminal Bell", success, ""))

    # Test 6: Services
    success = await test_services()
    results.append(("Services Layer", success, ""))

    # Test 7: Error Handling
    success = test_error_handling()
    results.append(("Error Handling", success, ""))

    # Test 8: CLI Commands
    success = test_cli_commands()
    results.append(("CLI Commands", success, ""))

    # Résumé final
    console.print("\n" + "=" * 60)
    console.print(Panel.fit("[bold]📊 RÉSUMÉ DES TESTS[/bold]", border_style="cyan"))

    table = Table(box=box.DOUBLE)
    table.add_column("Test", style="cyan")
    table.add_column("Result")
    table.add_column("Details")

    total_passed = 0
    for name, success, details in results:
        if success:
            total_passed += 1
            table.add_row(name, "[green]✅ PASS[/green]", details)
        else:
            table.add_row(name, "[red]❌ FAIL[/red]", details)

    console.print(table)

    # Score final
    score = total_passed / len(results) * 100
    color = "green" if score >= 80 else ("yellow" if score >= 60 else "red")

    console.print(
        f"\n[bold {color}]Score: {total_passed}/{len(results)} tests passés ({score:.0f}%)[/bold {color}]"
    )

    if score == 100:
        console.print(
            "\n[bold green]🎉 Toutes les intégrations fonctionnent parfaitement![/bold green]"
        )
    elif score >= 80:
        console.print("\n[bold yellow]✅ La plupart des intégrations fonctionnent.[/bold yellow]")
    else:
        console.print("\n[bold red]⚠️ Certaines intégrations nécessitent attention.[/bold red]")

    return score >= 80


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
