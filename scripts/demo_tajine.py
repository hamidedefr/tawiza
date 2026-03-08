#!/usr/bin/env python3
"""
TAJINE End-to-End Demo Script

Demonstrates the full PPDSL cycle with real-time progress display:
- Event-driven progress tracking
- Trust score evolution
- Tool execution with fallback
- Cognitive synthesis layers

Usage:
    python scripts/demo_tajine.py
    python scripts/demo_tajine.py --query "Analyse tech sector in 34"
    python scripts/demo_tajine.py --verbose --real-api
"""

import asyncio
import sys
from datetime import datetime
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from rich import box
from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn, TimeElapsedColumn
from rich.table import Table
from rich.text import Text

console = Console()


def create_header():
    """Create demo header."""
    return Panel(
        "[bold cyan]TAJINE Meta-Agent Demo[/]\n"
        "[dim]Territorial Analysis and Intelligence Engine[/]\n\n"
        "[bold]PPDSL Cycle:[/] Perceive → Plan → Delegate → Synthesize → Learn",
        title="[bold white]MPtoO v2[/]",
        border_style="cyan",
        box=box.DOUBLE,
    )


def create_event_log_panel(events: list) -> Panel:
    """Create scrolling event log panel."""
    if not events:
        content = "[dim]Waiting for events...[/]"
    else:
        lines = []
        for ev in events[-12:]:  # Show last 12 events
            icon = {
                "perceive": "👁️",
                "plan": "📋",
                "delegate": "🔧",
                "synthesize": "🧠",
                "learn": "📚",
            }.get(ev.get("phase", ""), "⚙️")

            phase = ev.get("phase", "init")[:10].ljust(10)
            msg = ev.get("message", "")[:45]
            progress = ev.get("progress", 0)

            lines.append(f"  {icon} [{phase}] {progress:3d}% │ {msg}")

        content = "\n".join(lines)

    return Panel(
        content,
        title="[bold]Event Log[/]",
        border_style="blue",
    )


def create_metrics_panel(metrics: dict) -> Panel:
    """Create metrics panel showing trust and performance."""
    table = Table(show_header=False, box=None, padding=(0, 1))
    table.add_column("Key", style="dim")
    table.add_column("Value", justify="right")

    trust = metrics.get("trust_score", 0.5)
    trust_color = "green" if trust > 0.7 else "yellow" if trust > 0.4 else "red"

    table.add_row("Trust Score", f"[{trust_color}]{trust:.2f}[/]")
    table.add_row("Autonomy", metrics.get("autonomy_level", "ASSISTED"))
    table.add_row("Success Rate", f"{metrics.get('success_rate', 0):.1%}")
    table.add_row("Successes", str(metrics.get("success_count", 0)))
    table.add_row("Failures", str(metrics.get("failure_count", 0)))

    return Panel(
        table,
        title="[bold]Trust Metrics[/]",
        border_style="green",
    )


def create_current_phase_panel(phase: str, message: str, thinking: str = "") -> Panel:
    """Create panel showing current phase activity."""
    phase_icons = {
        "perceive": ("👁️", "cyan", "Analyzing intent and context"),
        "plan": ("📋", "yellow", "Decomposing into subtasks"),
        "delegate": ("🔧", "magenta", "Executing via tool registry"),
        "synthesize": ("🧠", "blue", "Aggregating through cognitive layers"),
        "learn": ("📚", "green", "Updating trust metrics"),
    }

    icon, color, desc = phase_icons.get(phase, ("⚙️", "white", "Processing"))

    content = f"[bold {color}]{icon} {phase.upper()}[/]\n\n"
    content += f"[{color}]{desc}[/]\n\n"
    content += f"[dim]{message}[/]"

    if thinking:
        content += f"\n\n[italic dim]💭 {thinking}[/]"

    return Panel(
        content,
        title="[bold]Current Phase[/]",
        border_style=color,
    )


async def run_demo(query: str, verbose: bool = False, real_api: bool = False):
    """Run the TAJINE demo with real-time display."""
    from src.infrastructure.agents.tajine import TAJINEAgent
    from src.infrastructure.agents.tajine.events import TAJINECallback, TAJINEEvent

    # State for display
    events = []
    current_phase = {"phase": "", "message": "Initializing...", "thinking": ""}
    metrics = {
        "trust_score": 0.5,
        "autonomy_level": "ASSISTED",
        "success_rate": 0,
        "success_count": 0,
        "failure_count": 0,
    }

    # Create agent
    agent = TAJINEAgent(
        name="demo_tajine",
        local_model="qwen3:14b",
        powerful_model="qwen3:14b",
    )

    # Event handler
    def on_event(cb: TAJINECallback):
        events.append(
            {
                "phase": cb.phase,
                "message": cb.message,
                "progress": cb.progress,
                "event": cb.event.value,
                "data": cb.data,
            }
        )

        current_phase["phase"] = cb.phase or current_phase["phase"]
        current_phase["message"] = cb.message

        if cb.event == TAJINEEvent.THINKING:
            current_phase["thinking"] = cb.message

        # Update metrics from trust manager
        try:
            tm = agent.trust_manager
            metrics["trust_score"] = tm.get_trust_score()
            metrics["autonomy_level"] = tm.get_autonomy_level().name
            metrics["success_rate"] = tm.get_success_rate()
            metrics["success_count"] = tm.success_count
            metrics["failure_count"] = tm.failure_count
        except Exception:
            pass

    agent.on_event(on_event)

    # Create layout
    def create_layout():
        layout = Layout()
        layout.split_column(
            Layout(create_header(), size=7),
            Layout(name="main"),
            Layout(name="bottom", size=3),
        )
        layout["main"].split_row(
            Layout(create_event_log_panel(events), name="events"),
            Layout(name="right", ratio=1),
        )
        layout["right"].split_column(
            Layout(
                create_current_phase_panel(
                    current_phase["phase"], current_phase["message"], current_phase["thinking"]
                ),
                name="phase",
            ),
            Layout(create_metrics_panel(metrics), name="metrics", size=10),
        )

        # Bottom progress
        progress_pct = events[-1]["progress"] if events else 0
        progress_text = f"[bold cyan]Progress:[/] {progress_pct}% │ [dim]Query: {query[:50]}...[/]"
        layout["bottom"].update(Panel(progress_text, border_style="dim"))

        return layout

    # Run with live display
    console.print()
    console.print("[bold]Starting TAJINE Demo[/]")
    console.print(f"[dim]Query:[/] {query}")
    console.print(f"[dim]Real API:[/] {'Yes' if real_api else 'No (simulation)'}")
    console.print()

    task_config = {
        "prompt": query,
        "use_real_api": real_api,
    }

    with Live(create_layout(), refresh_per_second=4, console=console) as live:
        # Run the agent
        result = await agent.execute_task(task_config)

        # Final update
        live.update(create_layout())
        await asyncio.sleep(1)  # Brief pause to show final state

    # Display result
    console.print()

    if result.get("status") == "completed":
        confidence = result.get("confidence", 0)
        console.print(
            Panel(
                f"[bold green]Task Completed Successfully[/]\n\n"
                f"Task ID: {result.get('task_id')}\n"
                f"Confidence: {confidence:.1%}\n"
                f"Subtasks: {result.get('metadata', {}).get('subtask_count', 0)}\n"
                f"Final Trust: {result.get('metadata', {}).get('trust_score', 0):.2f}",
                title="[bold]Result[/]",
                border_style="green",
            )
        )

        # Show analysis if available
        if analysis := result.get("result"):
            console.print()
            console.print("[bold]Analysis:[/]")
            if isinstance(analysis, dict):
                for key, value in list(analysis.items())[:5]:
                    console.print(f"  [cyan]{key}:[/] {str(value)[:60]}...")
            else:
                console.print(f"  {str(analysis)[:200]}...")

        # Show cognitive levels
        if levels := result.get("cognitive_levels"):
            console.print()
            console.print("[bold]Cognitive Levels:[/]")
            for level, data in levels.items():
                if isinstance(data, dict) and data.get("summary"):
                    console.print(f"  [{level}] {data['summary'][:50]}...")
    else:
        console.print(
            Panel(
                f"[bold red]Task Failed[/]\n\nError: {result.get('error', 'Unknown')}",
                title="[bold]Result[/]",
                border_style="red",
            )
        )

    # Event summary
    if verbose:
        console.print()
        console.print("[bold]Event Summary:[/]")
        phase_counts = {}
        for ev in events:
            phase = ev.get("phase", "unknown")
            phase_counts[phase] = phase_counts.get(phase, 0) + 1

        for phase, count in phase_counts.items():
            console.print(f"  {phase}: {count} events")

    return result


async def demo_trust_evolution():
    """Demo showing trust score evolution over multiple tasks."""
    from src.infrastructure.agents.tajine import TAJINEAgent

    console.print()
    console.print(
        Panel(
            "[bold]Trust Evolution Demo[/]\n\n"
            "Running multiple tasks to show trust score adaptation.",
            border_style="yellow",
        )
    )

    agent = TAJINEAgent(name="trust_demo")

    queries = [
        "Analyse tech sector in 34",
        "Compare commerce in 75 vs 13",
        "Prospect biotech in Occitanie",
        "Monitor industry trends",
    ]

    trust_history = []

    for i, query in enumerate(queries, 1):
        console.print(f"\n[bold]Task {i}/{len(queries)}:[/] {query[:40]}...")

        result = await agent.execute_task({"prompt": query})

        trust = agent.trust_manager.get_trust_score()
        trust_history.append(trust)

        status = "[green]✓[/]" if result.get("status") == "completed" else "[red]✗[/]"
        console.print(
            f"  {status} Trust: {trust:.3f} ({agent.trust_manager.get_autonomy_level().name})"
        )

    # Summary
    console.print()
    console.print("[bold]Trust Evolution:[/]")
    for i, trust in enumerate(trust_history, 1):
        bar = "█" * int(trust * 20) + "░" * (20 - int(trust * 20))
        console.print(f"  Task {i}: [{bar}] {trust:.3f}")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="TAJINE Demo")
    parser.add_argument(
        "--query",
        "-q",
        default="Analyse le secteur tech dans le département 34",
        help="Query for analysis",
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Show verbose output")
    parser.add_argument("--real-api", action="store_true", help="Use real SIRENE API")
    parser.add_argument("--trust-demo", action="store_true", help="Run trust evolution demo")

    args = parser.parse_args()

    if args.trust_demo:
        asyncio.run(demo_trust_evolution())
    else:
        asyncio.run(
            run_demo(
                query=args.query,
                verbose=args.verbose,
                real_api=args.real_api,
            )
        )


if __name__ == "__main__":
    main()
