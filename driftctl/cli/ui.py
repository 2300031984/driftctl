from rich.align import Align
from rich.console import Console, Group
from rich.panel import Panel
from rich.text import Text


console = Console()


BANNER = r"""
██████╗ ██████╗ ██╗███████╗████████╗ ██████╗████████╗██╗
██╔══██╗██╔══██╗██║██╔════╝╚══██╔══╝██╔════╝╚══██╔══╝██║
██║  ██║██████╔╝██║█████╗     ██║   ██║        ██║   ██║
██║  ██║██╔══██╗██║██╔══╝     ██║   ██║        ██║   ██║
██████╔╝██║  ██║██║██║        ██║   ╚██████╗   ██║   ██║
╚═════╝ ╚═╝  ╚═╝╚═╝╚═╝        ╚═╝    ╚═════╝   ╚═╝   ╚═╝
"""


def show_banner() -> None:
    title = Text(BANNER, style="bold cyan")

    subtitle = Text(
        "Attack Surface Drift Detection",
        style="bold white",
    )

    tagline = Text(
        "Detect changes. Explain risk. Preserve evidence.",
        style="italic bright_cyan",
    )

    content = Group(
        Align.center(title),
        Align.center(subtitle),
        Align.center(tagline),
    )

    console.print(
        Panel(
            content,
            border_style="cyan",
            padding=(1, 2),
        )
    )


def show_info() -> None:
    console.print(
        Panel(
            "[bold cyan]DRIFTCTL[/bold cyan]\n"
            "Attack Surface Drift Detection CLI\n\n"
            "Detect changes in an authorized target's externally\n"
            "observable attack surface over time.",
            title="[bold white]About[/bold white]",
            border_style="cyan",
            padding=(1, 2),
        )
    )

    features = (
        "[bold cyan]FEATURES[/bold cyan]\n\n"
        "[green]●[/green] HTTP endpoint discovery\n"
        "[green]●[/green] Snapshot & diff analysis\n"
        "[green]●[/green] Security-aware risk classification\n"
        "[green]●[/green] Semantic security findings\n"
        "[green]●[/green] Historical tracking\n"
        "[green]●[/green] Evidence reconstruction\n"
        "[green]●[/green] Security baselines\n"
        "[green]●[/green] Anomaly detection"
    )

    console.print(
        Panel(
            features,
            border_style="green",
        )
    )

    quick_start = (
        "[bold cyan]QUICK START[/bold cyan]\n\n"
        "[dim]$[/dim] driftctl scan <TARGET>\n"
        "[dim]$[/dim] driftctl baseline <TARGET>\n"
        "[dim]$[/dim] driftctl diff <TARGET>\n"
        "[dim]$[/dim] driftctl history <TARGET>\n"
        "[dim]$[/dim] driftctl anomalies <TARGET>\n"
        "[dim]$[/dim] driftctl explain <FINDING_ID>\n"
        "[dim]$[/dim] driftctl evidence <FINDING_ID>\n\n"
        "[bold yellow]Example:[/bold yellow]\n"
        "[dim]$[/dim] driftctl scan 127.0.0.1:8080"
    )

    console.print(
        Panel(
            quick_start,
            border_style="yellow",
        )
    )

    workflow = (
        "[bold cyan]WORKFLOW[/bold cyan]\n\n"
        "[cyan]Target[/cyan]"
        " → "
        "[cyan]Snapshot[/cyan]"
        " → "
        "[cyan]Diff[/cyan]"
        " → "
        "[cyan]Risk[/cyan]"
        " → "
        "[cyan]Finding[/cyan]"
        " → "
        "[cyan]Evidence[/cyan]"
    )

    console.print(
        Panel(
            Align.center(workflow),
            border_style="magenta",
        )
    )

    console.print()

    console.print(
        Panel(
            "[bold red]AUTHORIZED USE ONLY[/bold red]\n\n"
            "Use DriftCTL only against systems you own "
            "or have explicit permission to assess.",
            border_style="red",
        )
    )

    console.print()
    footer = Text()
    footer.append("DriftCTL ", style="bold cyan")
    footer.append("v1.1.0-dev", style="bold white")
    footer.append("  •  ", style="dim")
    footer.append(
        "Authorized security testing only",
        style="dim",
    )

    console.print(Align.center(footer))


def show_welcome() -> None:
    console.clear()

    show_banner()

    console.print()

    show_info()

    console.print()
