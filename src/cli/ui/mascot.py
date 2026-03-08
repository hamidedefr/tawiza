"""MPtoO CLI Mascot - ASCII Art Cat Assistant (Detailed Version)."""

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

# Mascotte détaillée - Chat réaliste
MPTOO_CAT_DETAILED = r"""
                          ╱|、
                        (˚ˎ 。7
                         |、˜〵
                         じしˍ,)ノ
"""

MPTOO_CAT_LAPTOP = r"""
                    ╱|、
                  (˚ˎ 。7
                   |、˜〵
            ┌──────じしˍ,)──────┐
            │  ┌─────────────┐  │
            │  │ MPtoO v2.0  │  │
            │  │   >>> _     │  │
            │  └─────────────┘  │
            └───────────────────┘
"""

MPTOO_CAT_REALISTIC = r"""
               ,_     _,
               |\\___//|
               |=6   6=|
               \=._Y_.=/
                )  `  (    ,
               /       \  ((
               |       |   ))
              /| |   | |\_//
              \| |._.| |/-`
               '"'   '"'
"""

MPTOO_CAT_CODER = r"""
               ,_     _,
               |\\___//|
               |=6   6=|    ┌─────────────────┐
               \=._Y_.=/    │ MPtoO-V2        │
                )  `  ( ────│ AI Multi-Agent  │
               /       \    │ Platform 🌅     │
               |  ___  |    └─────────────────┘
              /| /   \ |\
              \|/_____\|/
               '"'   '"'
"""

MPTOO_CAT_HACKER = r"""
            ▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄
            █  ,_     _,         █
            █  |\\___//|  MPtoO  █
            █  |=o   o=|  v2.0   █
            █  \=._Y_.=/  ━━━━━  █
            █   )  `  (   🌅     █
            █  /       \  GPU    █
            █▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄█
"""

MPTOO_CAT_STYLIZED = r"""
        ╭━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╮
        ┃           ,_     _,              ┃
        ┃           |\\___//|              ┃
        ┃           |=○   ○=|              ┃
        ┃           \=._Y_.=/              ┃
        ┃            )  `  (               ┃
        ┃           /       \              ┃
        ┃          |   MPtoO |             ┃
        ╰━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╯
"""

MPTOO_CAT_WELCOME_DETAILED = r"""
    ╔══════════════════════════════════════════════════════╗
    ║                                                      ║
    ║              ,_     _,                               ║
    ║              |\\___//|      🌅 MPtoO-V2              ║
    ║              |=○   ○=|      ═══════════════          ║
    ║              \=._Y_.=/      Multi-Agent AI System    ║
    ║               )  `  (       GPU Optimized Platform   ║
    ║              /       \                               ║
    ║             |    ◡    |     Ready to assist! ✨      ║
    ║                                                      ║
    ╚══════════════════════════════════════════════════════╝
"""

MPTOO_BANNER_FULL = r"""

    ╔═══════════════════════════════════════════════════════════════╗
    ║                                                               ║
    ║   ███╗   ███╗██████╗ ████████╗ ██████╗  ██████╗               ║
    ║   ████╗ ████║██╔══██╗╚══██╔══╝██╔═══██╗██╔═══██╗              ║
    ║   ██╔████╔██║██████╔╝   ██║   ██║   ██║██║   ██║              ║
    ║   ██║╚██╔╝██║██╔═══╝    ██║   ██║   ██║██║   ██║              ║
    ║   ██║ ╚═╝ ██║██║        ██║   ╚██████╔╝╚██████╔╝              ║
    ║   ╚═╝     ╚═╝╚═╝        ╚═╝    ╚═════╝  ╚═════╝               ║
    ║                                                               ║
    ║          ,_     _,     Multi-Platform to Ollama               ║
    ║          |\\___//|     Advanced AI Agents System              ║
    ║          |=○   ○=|     ══════════════════════════             ║
    ║          \=._Y_.=/     🌅 Sunset Theme Edition                ║
    ║           )  `  (      🚀 GPU Optimized                       ║
    ║          /       \     🤖 Multi-Agent Platform                ║
    ║                                                               ║
    ╚═══════════════════════════════════════════════════════════════╝

"""

MPTOO_CAT_MOODS = {
    "default": r"""
              ,_     _,
              |\\___//|
              |=○   ○=|
              \=._Y_.=/
               )  `  (
              /       \
""",
    "happy": r"""
              ,_     _,
              |\\___//|
              |=^   ^=|
              \=._◡_.=/
               )  `  ( ✨
              /       \
""",
    "thinking": r"""
              ,_     _,   💭
              |\\___//|  ?
              |=◔   ◔=|
              \=._~_.=/
               )  `  (
              /       \
""",
    "working": r"""
              ,_     _,  ⚡
              |\\___//|
              |=▶   ◀=|
              \=._△_.=/  ⚙️
               )  `  (
              /  ███  \
""",
    "coding": r"""
              ,_     _,
              |\\___//|    ┌────────┐
              |=●   ●=| ───│ </>    │
              \=._Y_.=/    └────────┘
               )  `  (
              /       \
""",
    "sleeping": r"""
              ,_     _,
              |\\___//|  z
              |=-   -=|   z
              \=._◡_.=/    z
               )  `  (
              /       \
""",
    "error": r"""
              ,_     _,  ❌
              |\\___//|
              |=X   X=|
              \=._▽_.=/
               )  `  (
              /       \
""",
    "success": r"""
              ,_     _,  ✅
              |\\___//|
              |=★   ★=|
              \=._◡_.=/
               )  `  ( 🎉
              /       \
"""
}

# Mini mascotte pour les messages courts
MPTOO_MINI = r"""(=^･ω･^=)"""
MPTOO_MINI_HAPPY = r"""(=^◡^=)"""
MPTOO_MINI_SAD = r"""(=;ェ;=)"""
MPTOO_MINI_WORKING = r"""(=^･ｪ･^=)⚙️"""


def get_mascot(mood: str = "default") -> str:
    """Get mascot ASCII art based on mood."""
    return MPTOO_CAT_MOODS.get(mood, MPTOO_CAT_MOODS["default"])


def get_detailed_mascot(style: str = "default") -> str:
    """Get detailed mascot art."""
    styles = {
        "default": MPTOO_CAT_DETAILED,
        "laptop": MPTOO_CAT_LAPTOP,
        "realistic": MPTOO_CAT_REALISTIC,
        "coder": MPTOO_CAT_CODER,
        "hacker": MPTOO_CAT_HACKER,
        "stylized": MPTOO_CAT_STYLIZED,
        "welcome": MPTOO_CAT_WELCOME_DETAILED,
        "banner": MPTOO_BANNER_FULL,
    }
    return styles.get(style, MPTOO_CAT_DETAILED)


def print_mascot(
    mood: str = "default",
    message: str = None,
    style: str = "cyan",
    console: Console = None
):
    """Print mascot with optional message."""
    if console is None:
        console = Console()

    mascot_art = get_mascot(mood)

    if message:
        content = Text()
        content.append(mascot_art, style=style)
        content.append(f"\n{message}", style="bold white")
        console.print(Panel(content, border_style=style))
    else:
        console.print(mascot_art, style=style)


def print_welcome(console: Console = None):
    """Print welcome banner with mascot."""
    if console is None:
        console = Console()
    console.print(MPTOO_CAT_WELCOME_DETAILED, style="bold cyan")


def print_banner(console: Console = None):
    """Print full banner with logo and mascot."""
    if console is None:
        console = Console()

    lines = MPTOO_BANNER_FULL.split('\n')
    colors = ["#FF6B6B", "#FF8E72", "#FFB347", "#87CEEB", "#DDA0DD", "#98D8C8"]

    for i, line in enumerate(lines):
        if "███" in line or "═" in line:
            console.print(line, style=colors[i % len(colors)])
        elif "○" in line or "\\\\" in line or "_," in line:
            console.print(line, style="yellow")
        else:
            console.print(line, style="cyan")


def mascot_says(message: str, mood: str = "default", console: Console = None):
    """Display mascot with a speech bubble message."""
    if console is None:
        console = Console()

    mascot = get_mascot(mood)

    # Speech bubble
    msg_len = len(message)
    padding = max(msg_len + 4, 24)

    console.print("╭" + "─" * padding + "╮", style="dim cyan")
    console.print(f"│ {message.center(padding - 2)} │", style="cyan")
    console.print("╰" + "─" * padding + "╯", style="dim cyan")
    console.print("        ╲", style="dim cyan")
    console.print(mascot, style="yellow")


def mini_mascot(mood: str = "default") -> str:
    """Get mini inline mascot."""
    minis = {
        "default": MPTOO_MINI,
        "happy": MPTOO_MINI_HAPPY,
        "sad": MPTOO_MINI_SAD,
        "working": MPTOO_MINI_WORKING,
    }
    return minis.get(mood, MPTOO_MINI)


# CLI Integration helpers
def startup_mascot(console: Console = None):
    """Show mascot on CLI startup."""
    if console is None:
        console = Console()
    console.print(get_detailed_mascot("coder"), style="yellow")


def error_mascot(message: str, console: Console = None):
    """Show error mascot with message."""
    if console is None:
        console = Console()
    mascot_says(message, "error", console)


def success_mascot(message: str, console: Console = None):
    """Show success mascot with message."""
    if console is None:
        console = Console()
    mascot_says(message, "success", console)


if __name__ == "__main__":
    console = Console()

    console.print("\n[bold magenta]═══ MPtoO Mascot Gallery ═══[/bold magenta]\n")

    console.print("[bold cyan]▸ Detailed Styles:[/bold cyan]\n")

    for style in ["realistic", "coder", "hacker", "laptop"]:
        console.print(f"[yellow]{style.upper()}:[/yellow]")
        console.print(get_detailed_mascot(style), style="cyan")
        console.print()

    console.print("[bold cyan]▸ Mood Variants:[/bold cyan]\n")

    for mood in ["default", "happy", "thinking", "working", "success", "error"]:
        console.print(f"[yellow]{mood}:[/yellow]")
        print_mascot(mood)
        console.print()

    console.print("[bold cyan]▸ Welcome Banner:[/bold cyan]")
    print_welcome()

    console.print("\n[bold cyan]▸ Speech Bubble:[/bold cyan]")
    mascot_says("Bienvenue sur MPtoO-V2!", "happy")

    console.print("\n[bold cyan]▸ Full Banner:[/bold cyan]")
    print_banner()

    console.print("\n[bold cyan]▸ Mini Mascots:[/bold cyan]")
    console.print(f"  Default: {mini_mascot('default')}")
    console.print(f"  Happy:   {mini_mascot('happy')}")
    console.print(f"  Working: {mini_mascot('working')}")
