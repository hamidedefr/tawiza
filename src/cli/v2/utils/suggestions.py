"""Smart suggestions for MPtoO CLI v2."""

from dataclasses import dataclass

from rich.console import Console

from src.cli.v2.ui.theme import THEME


@dataclass
class Suggestion:
    """A command suggestion."""
    command: str
    description: str
    priority: int = 0  # Higher = more relevant


# Command flow graph - what comes after what
COMMAND_FLOWS: dict[str, list[Suggestion]] = {
    # After status
    "status": [
        Suggestion("mptoo chat", "Start chatting with AI", 10),
        Suggestion("mptoo run analyst", "Run data analysis agent", 8),
        Suggestion("mptoo pro doctor", "Run system diagnostics", 5),
    ],

    # After chat
    "chat": [
        Suggestion("mptoo run coder", "Run coding agent on your idea", 10),
        Suggestion("mptoo pro model-list", "See available models", 5),
    ],

    # After run
    "run": [
        Suggestion("mptoo status", "Check system status", 8),
        Suggestion("mptoo pro logs-show", "View execution logs", 7),
    ],

    # After agent
    "agent": [
        Suggestion("mptoo agent \"Another task\"", "Run another autonomous task", 10),
        Suggestion("mptoo run analyst", "Run a specific agent", 8),
        Suggestion("mptoo pro logs-show", "View execution logs", 7),
    ],

    # After model operations
    "pro model-list": [
        Suggestion("mptoo pro model-pull <model>", "Download a new model", 10),
        Suggestion("mptoo chat -m <model>", "Chat with a specific model", 8),
    ],
    "pro model-pull": [
        Suggestion("mptoo pro model-list", "Verify model installed", 10),
        Suggestion("mptoo chat", "Start using the model", 8),
    ],

    # After GPU operations
    "pro gpu-info": [
        Suggestion("mptoo pro gpu-benchmark", "Run GPU benchmark", 10),
        Suggestion("mptoo pro gpu-passthrough-status", "Check passthrough config", 8),
    ],
    "pro gpu-passthrough-enable": [
        Suggestion("reboot", "Reboot to apply changes", 10),
        Suggestion("mptoo pro gpu-vm-list", "Check VM GPU assignments", 5),
    ],
    "pro gpu-passthrough-disable": [
        Suggestion("reboot", "Reboot to use GPU on host", 10),
    ],

    # After data operations
    "pro data-import": [
        Suggestion("mptoo pro data-list", "Verify import", 10),
        Suggestion("mptoo pro train-start", "Start training on data", 8),
    ],
    "pro data-list": [
        Suggestion("mptoo pro data-import <file>", "Import new dataset", 8),
        Suggestion("mptoo pro train-start", "Train on a dataset", 7),
    ],

    # After training
    "pro train-start": [
        Suggestion("mptoo pro train-status", "Monitor training progress", 10),
        Suggestion("mptoo pro gpu-monitor", "Watch GPU usage", 8),
    ],
    "pro train-status": [
        Suggestion("mptoo pro train-stop <id>", "Stop a running job", 5),
        Suggestion("mptoo pro logs-show", "View training logs", 7),
    ],

    # After config
    "pro config-show": [
        Suggestion("mptoo pro config-set <key> <value>", "Change a setting", 10),
        Suggestion("mptoo pro config-edit", "Interactive config editor", 8),
    ],
    "pro config-set": [
        Suggestion("mptoo pro config-show", "Verify changes", 10),
    ],

    # After system commands
    "pro doctor": [
        Suggestion("mptoo pro ollama-start", "Start Ollama if not running", 8),
        Suggestion("mptoo pro cache-clear", "Clear cache if issues", 5),
    ],
    "pro cache-clear": [
        Suggestion("mptoo status", "Verify system status", 8),
    ],

    # After ollama
    "pro ollama-start": [
        Suggestion("mptoo pro model-list", "Check available models", 10),
        Suggestion("mptoo chat", "Start chatting", 8),
    ],
    "pro ollama-stop": [
        Suggestion("mptoo pro ollama-start", "Restart Ollama", 5),
    ],
}

# Context-aware suggestions based on system state
CONTEXTUAL_SUGGESTIONS: dict[str, callable] = {}


def _check_ollama_running() -> bool:
    """Check if Ollama is running."""
    try:
        import httpx
        response = httpx.get("http://localhost:11434/api/tags", timeout=2)
        return response.status_code == 200
    except Exception:
        return False


def _check_gpu_available() -> bool:
    """Check if GPU is available on host."""
    try:
        import subprocess
        result = subprocess.run(["rocm-smi", "--showid"], capture_output=True, timeout=5)
        return result.returncode == 0
    except Exception:
        return False


def get_suggestions(last_command: str, context: dict = None) -> list[Suggestion]:
    """Get suggestions based on last command and context."""
    suggestions = []

    # Get flow-based suggestions
    if last_command in COMMAND_FLOWS:
        suggestions.extend(COMMAND_FLOWS[last_command])

    # Add contextual suggestions
    if not _check_ollama_running():
        suggestions.append(Suggestion(
            "mptoo pro ollama-start",
            "Ollama not running - start it",
            priority=15
        ))

    # Sort by priority
    suggestions.sort(key=lambda s: s.priority, reverse=True)

    return suggestions[:3]  # Return top 3


def print_suggestions(last_command: str, console: Console = None):
    """Print suggestions after command execution."""
    if console is None:
        console = Console()

    suggestions = get_suggestions(last_command)

    if not suggestions:
        return

    console.print()
    console.print("  [dim]┌─ Next steps ─────────────────────────[/]")

    for i, s in enumerate(suggestions, 1):
        console.print(f"  [dim]│[/] [{THEME['accent']}]{i}.[/] {s.command}")
        console.print(f"  [dim]│[/]    [dim]{s.description}[/]")

    console.print("  [dim]└──────────────────────────────────────[/]")


# Command examples for help text
COMMAND_EXAMPLES: dict[str, list[str]] = {
    "chat": [
        "mptoo chat                     # Interactive chat",
        "mptoo chat 'Hello!'            # Quick message",
        "mptoo chat -m llama3:8b        # Use specific model",
    ],
    "run": [
        "mptoo run analyst              # Interactive agent selection",
        "mptoo run coder -t 'Fix bug'   # Run with task",
        "mptoo run ml -d data.csv       # Process data file",
    ],
    "agent": [
        "mptoo agent 'What time is it in Tokyo?'  # Simple task",
        "mptoo agent 'Analyze trends' -d data.csv # With data",
        "mptoo agent 'Scrape HN' -v               # Verbose mode",
    ],
    "status": [
        "mptoo status                   # Quick status",
        "mptoo status -v                # Detailed status",
    ],
    "pro model-list": [
        "mptoo pro model-list           # List all models",
    ],
    "pro model-pull": [
        "mptoo pro model-pull qwen3.5:27b # Pull recommended model",
        "mptoo pro model-pull llama3:70b # Pull large model",
    ],
    "pro gpu-info": [
        "mptoo pro gpu-info             # Basic GPU info",
        "mptoo pro gpu-info -v          # With IOMMU groups",
    ],
    "pro train-start": [
        "mptoo pro train-start qwen3.5:27b -d data.jsonl",
        "mptoo pro train-start llama3:8b -d train.csv -e 5",
    ],
    "pro config-set": [
        "mptoo pro config-set model qwen3:30b",
        "mptoo pro config-set timeout 120",
    ],
    "pro data-import": [
        "mptoo pro data-import data.csv",
        "mptoo pro data-import train.jsonl -n my-dataset",
    ],
}


def get_examples(command: str) -> list[str]:
    """Get examples for a command."""
    return COMMAND_EXAMPLES.get(command, [])


def format_examples(command: str) -> str:
    """Format examples for display in help."""
    examples = get_examples(command)
    if not examples:
        return ""

    lines = ["\n[bold]Examples:[/]"]
    for ex in examples:
        lines.append(f"  [dim]{ex}[/]")

    return "\n".join(lines)
