import argparse
import re
from pathlib import Path

from rich.console import Console

from driftctl.core.evidence import build_evidence
from driftctl.core.explain import build_explanation
from driftctl.collectors.http import collect_http
from driftctl.core.diff import compare_snapshots
from driftctl.core.findings import create_finding
from driftctl.core.history import build_history
from driftctl.core.models import Snapshot
from driftctl.storage.findings import (
    find_by_fingerprint,
    list_findings,
    load_finding,
    migrate_legacy_findings,
    save_finding,
)
from driftctl.storage.snapshots import (
    list_snapshots,
    load_snapshot,
    save_snapshot,
)
from driftctl.core.anomaly import detect_anomalies
from driftctl.core.baseline import (
    create_baseline,
    load_baseline,
    save_baseline,
)

console = Console()


def create_snapshot(target: str):
    console.print(
        f"[bold cyan][+] Creating snapshot for {target}[/bold cyan]"
    )

    observations = collect_http(
        f"http://{target}"
    )

    snapshot = Snapshot.create(
        target=target,
        observations=observations,
    )

    path = save_snapshot(snapshot)

    console.print(
        f"[green][+] Snapshot saved:[/green] {path}"
    )


def next_finding_id() -> str:
    highest = 0

    for path in list_findings():

        match = re.fullmatch(
            r"CHANGE-(\d+)",
            path.stem,
        )

        if match:
            number = int(match.group(1))
            highest = max(highest, number)

    return f"CHANGE-{highest + 1:04d}"


def show_diff(target: str):

    snapshots = list_snapshots(target)

    if len(snapshots) < 2:
        console.print(
            "[yellow]Need at least two snapshots to compare.[/yellow]"
        )
        return

    previous_path = snapshots[-2]
    current_path = snapshots[-1]

    previous = load_snapshot(previous_path)
    current = load_snapshot(current_path)

    changes = compare_snapshots(
        previous,
        current,
    )

    console.print()
    console.print(
        "[bold cyan]Comparing:[/bold cyan]"
    )

    console.print(
        f"  Previous: {previous_path.name}"
    )

    console.print(
        f"  Current:  {current_path.name}"
    )

    console.print()

    if not changes:
        console.print(
            "[green]No changes detected.[/green]"
        )
        return

    for change in changes:

        candidate = create_finding(
            change=change,
            target=target,
            finding_id="TEMP",
        )

        existing = find_by_fingerprint(
            candidate.fingerprint
        )

        if existing:

            console.print(
                f"[dim][SKIPPED] "
                f"{existing.id} already recorded: "
                f"{change.value}[/dim]"
            )

            continue

        finding = create_finding(
            change=change,
            target=target,
            finding_id=next_finding_id(),
        )

        path = save_finding(
            finding
        )

        if finding.risk == "HIGH":
            style = "bold red"

        elif finding.risk == "MEDIUM":
            style = "bold yellow"

        else:
            style = "green"

        console.print(
            f"[{style}]"
            f"[{finding.risk}] "
            f"[{finding.id}] "
            f"[{finding.change_type}] "
            f"{finding.value}"
            f"[/{style}]"
        )

        console.print(
            f"    Reason: {finding.reason}"
        )

        if finding.change_type == "CHANGED":

            console.print(
                f"    Previous: {finding.previous}"
            )

            console.print(
                f"    Current: {finding.current}"
            )

        console.print(
            f"    Evidence: {path}"
        )

        console.print()


def show_history(target: str):

    events = build_history(target)

    console.print()
    console.print(
        f"[bold cyan]Attack Surface History: {target}[/bold cyan]"
    )
    console.print()

    if not events:
        console.print(
            "[yellow]No historical changes found.[/yellow]"
        )
        return

    for event in events:

        timestamp = event.current_snapshot.stem.split(
            "_"
        )[-1]

        if event.risk == "HIGH":
            style = "bold red"

        elif event.risk == "MEDIUM":
            style = "bold yellow"

        else:
            style = "green"

        console.print(
            f"[bold cyan]{timestamp}[/bold cyan]"
        )

        console.print(
            f"  [{style}]"
            f"[{event.risk}] "
            f"{event.change_type} "
            f"{event.value}"
            f"[/{style}]"
        )

        console.print(
            f"    Reason: {event.reason}"
        )

        if event.finding_id:

            console.print(
                f"    Finding: {event.finding_id}"
            )

        else:

            console.print(
                "    Finding: Not persisted"
            )

        if event.change_type == "CHANGED":

            console.print(
                f"    Previous: {event.previous}"
            )

            console.print(
                f"    Current:  {event.current}"
            )

        console.print()

def migrate_findings():

    migrated = migrate_legacy_findings()

    console.print()

    if not migrated:
        console.print(
            "[green]No legacy findings require migration.[/green]"
        )
        return

    console.print(
        "[bold cyan]Migrated legacy findings:[/bold cyan]"
    )

    for finding_id in migrated:
        console.print(
            f"  [green]✓[/green] {finding_id}"
        )

    console.print()

    console.print(
        f"[green]Successfully migrated "
        f"{len(migrated)} finding(s).[/green]"
    )

def show_explanation(finding_id: str):

    try:
        finding = load_finding(
            finding_id
        )

    except FileNotFoundError:

        console.print(
            f"[red]Finding not found: {finding_id}[/red]"
        )
        return

    explanation = build_explanation(
        finding
    )

    console.print()
    console.print(
        f"[bold cyan]Finding: "
        f"{explanation['finding_id']}[/bold cyan]"
    )

    console.print(
        f"Target: {explanation['target']}"
    )

    console.print(
        f"Risk: [bold red]{explanation['risk']}[/bold red]"
        if explanation["risk"] == "HIGH"
        else f"Risk: [bold yellow]{explanation['risk']}[/bold yellow]"
        if explanation["risk"] == "MEDIUM"
        else f"Risk: {explanation['risk']}"
    )

    console.print()

    console.print("[bold]Change[/bold]")

    console.print(
        f"  Type: {explanation['change']['type']}"
    )

    console.print(
        f"  Value: {explanation['change']['value']}"
    )

    console.print()

    console.print("[bold]Why it matters[/bold]")

    console.print(
        f"  {explanation['reason']}"
    )

    console.print()

    console.print("[bold]Security significance[/bold]")

    console.print(
        f"  {explanation['security_significance']}"
    )

    console.print()

    console.print("[bold]Evidence[/bold]")

    console.print(
        f"  Previous: {explanation['evidence']['previous']}"
    )

    console.print(
        f"  Current:  {explanation['evidence']['current']}"
    )

    console.print()

    console.print("[bold]Recommended action[/bold]")

    console.print(
        f"  {explanation['recommendation']}"
    )

    console.print()

    console.print(
        f"[dim]Fingerprint: "
        f"{explanation['fingerprint']}[/dim]"
    )

    console.print(
        f"[dim]Detected: "
        f"{explanation['detected_at']}[/dim]"
    )

    console.print()


def show_evidence(finding_id: str):

    try:
        finding = load_finding(
            finding_id
        )

    except FileNotFoundError:

        console.print(
            f"[red]Finding not found: {finding_id}[/red]"
        )
        return

    evidence = build_evidence(
        finding
    )

    console.print()

    if evidence is None:

        console.print(
            "[yellow]Evidence could not be reconstructed "
            "from the available snapshots.[/yellow]"
        )

        return

    console.print(
        f"[bold cyan]Evidence: "
        f"{evidence['finding_id']}[/bold cyan]"
    )

    console.print()

    console.print(
        f"Target: {evidence['target']}"
    )

    console.print(
        f"Risk: {evidence['risk']}"
    )

    console.print()

    console.print(
        "[bold]Snapshot Pair[/bold]"
    )

    console.print(
        f"  Previous: "
        f"{Path(evidence['previous_snapshot']).name}"
    )

    console.print(
        f"  Current:  "
        f"{Path(evidence['current_snapshot']).name}"
    )

    console.print()

    console.print(
        "[bold]Observed Change[/bold]"
    )

    console.print(
        f"  Type: "
        f"{evidence['change_type']}"
    )

    console.print(
        f"  Observation: "
        f"{evidence['observation_type']}"
    )

    console.print(
        f"  Value: "
        f"{evidence['value']}"
    )

    console.print()

    console.print(
        "[bold]Previous Observation[/bold]"
    )

    console.print(
        f"  {evidence['previous']}"
    )

    console.print()

    console.print(
        "[bold]Current Observation[/bold]"
    )

    console.print(
        f"  {evidence['current']}"
    )

    console.print()

    console.print(
        "[bold]Risk Reason[/bold]"
    )

    console.print(
        f"  {evidence['reason']}"
    )

    console.print()

    console.print(
        f"[dim]Fingerprint: "
        f"{evidence['fingerprint']}[/dim]"
    )

    console.print()

def create_baseline_command(target: str):

    snapshots = list_snapshots(target)

    if not snapshots:

        console.print(
            "[yellow]No snapshots found for target.[/yellow]"
        )

        console.print(
            "Run 'driftctl scan "
            f"{target}' first."
        )

        return

    latest_snapshot_path = snapshots[-1]

    snapshot = load_snapshot(
        latest_snapshot_path
    )

    baseline = create_baseline(
        snapshot
    )

    path = save_baseline(
        baseline
    )

    console.print()

    console.print(
        "[bold cyan][+] Baseline created[/bold cyan]"
    )

    console.print(
        f"  Target: {target}"
    )

    console.print(
        f"  Snapshot: "
        f"{latest_snapshot_path.name}"
    )

    console.print(
        f"  Observations: "
        f"{len(baseline.observations)}"
    )

    console.print(
        f"  Saved: {path}"
    )

    console.print()

def show_anomalies(target: str):

    try:
        baseline = load_baseline(target)

    except FileNotFoundError:

        console.print(
            "[yellow]No baseline found for target.[/yellow]"
        )

        console.print(
            "Run 'driftctl baseline "
            f"{target}' first."
        )

        return

    snapshots = list_snapshots(target)

    if not snapshots:

        console.print(
            "[yellow]No snapshots found for target.[/yellow]"
        )

        console.print(
            "Run 'driftctl scan "
            f"{target}' first."
        )

        return

    latest_snapshot_path = snapshots[-1]

    snapshot = load_snapshot(
        latest_snapshot_path
    )

    anomalies = detect_anomalies(
        baseline,
        snapshot,
    )

    console.print()

    console.print(
        f"[bold cyan]Attack Surface Anomalies: "
        f"{target}[/bold cyan]"
    )

    console.print()

    console.print(
        f"Baseline created: "
        f"{baseline.created_at}"
    )

    console.print(
        f"Latest snapshot: "
        f"{latest_snapshot_path.name}"
    )

    console.print()

    if not anomalies:

        console.print(
            "[green]✓ No anomalies detected.[/green]"
        )

        console.print()

        return

    console.print(
        f"[bold]Detected {len(anomalies)} "
        f"anomaly(s)[/bold]"
    )

    console.print()

    for anomaly in anomalies:

        if anomaly.risk == "HIGH":
            style = "bold red"

        elif anomaly.risk == "MEDIUM":
            style = "bold yellow"

        else:
            style = "green"

        console.print(
            f"[{style}]"
            f"[{anomaly.risk}] "
            f"{anomaly.anomaly_type} "
            f"{anomaly.value}"
            f"[/{style}]"
        )

        console.print(
            f"    Observation: "
            f"{anomaly.observation_type}"
        )

        console.print(
            f"    Reason: "
            f"{anomaly.reason}"
        )

        if anomaly.baseline is not None:

            console.print(
                f"    Baseline: "
                f"{anomaly.baseline}"
            )

        if anomaly.current is not None:

            console.print(
                f"    Current: "
                f"{anomaly.current}"
            )

        console.print()


def main():

    parser = argparse.ArgumentParser(
        prog="driftctl",
        description="Attack Surface Drift Detection CLI",
    )

    subparsers = parser.add_subparsers(
        dest="command"
    )

    scan_parser = subparsers.add_parser(
        "scan",
        help="Create a new snapshot",
    )

    scan_parser.add_argument(
        "target",
        help="Authorized target",
    )

    diff_parser = subparsers.add_parser(
        "diff",
        help="Compare the two most recent snapshots",
    )

    diff_parser.add_argument(
        "target",
        help="Target to compare",
    )

    history_parser = subparsers.add_parser(
        "history",
        help="Show attack surface changes across all snapshots",
    )
    
    migrate_parser = subparsers.add_parser(
        "migrate-findings",
        help="Add fingerprints to legacy findings",
    )
    
    explain_parser = subparsers.add_parser(
        "explain",
        help="Explain a security finding",
    )

    explain_parser.add_argument(
        "finding_id",
        help="Finding ID such as CHANGE-0001",
    )

    evidence_parser = subparsers.add_parser(
        "evidence",
        help="Show evidence for a security finding",
    )

    evidence_parser.add_argument(
        "finding_id",
        help="Finding ID such as CHANGE-0001",
    )

    baseline_parser = subparsers.add_parser(
        "baseline",
        help="Create a baseline from the latest snapshot",
    )

    baseline_parser.add_argument(
        "target",
        help="Target to baseline",
    )
    
    anomalies_parser = subparsers.add_parser(
        "anomalies",
        help="Compare the latest snapshot against the baseline",
    )

    anomalies_parser.add_argument(
        "target",
        help="Target to inspect",
    )

    history_parser.add_argument(
        "target",
        help="Target to inspect",
    )

    args = parser.parse_args()

    if args.command == "scan":
        create_snapshot(args.target)

    elif args.command == "baseline":
        create_baseline_command(
            args.target
        )
    elif args.command == "anomalies":
        show_anomalies(
            args.target
        )

    elif args.command == "diff":
        show_diff(args.target)

    elif args.command == "history":
        show_history(args.target)
    
    elif args.command == "migrate-findings":
        migrate_findings()
     
    elif args.command == "explain":
        show_explanation(args.finding_id)

    elif args.command == "evidence":
        show_evidence(args.finding_id)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
