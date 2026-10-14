# Understanding DriftCTL Findings

DriftCTL compares observations from different snapshots to highlight changes in an application's externally observable attack surface. A difference is evidence of change, not by itself proof of compromise.

## Change types

- `NEW`: an asset or endpoint was observed that was not present in the earlier snapshot.
- `REMOVED`: an asset or endpoint observed earlier was not present in the later snapshot.
- `CHANGED`: an existing observation differs between snapshots.

Interpret each result in the context of the target, expected application behavior, and the time the snapshots were captured.

## Interpreting directional HTTP changes

Authentication and authorization changes should be interpreted directionally. For example, a transition from `401 Unauthorized` or `403 Forbidden` to `200 OK` can indicate that a previously restricted endpoint now responds successfully and deserves investigation. A transition from `200 OK` to `401` or `403` may indicate a tightened control rather than a security regression.

A status-code transition alone does not prove that authentication is absent or correctly enforced. Confirm the behavior with an authorized, controlled test and review the response and application configuration.

## Baselines and anomalies

A baseline records the expected state represented by a snapshot. An anomaly is a difference between the latest observation and that baseline. Keep the baseline representative of an approved, known-good state and refresh it deliberately after reviewed application changes; do not automatically accept every change as normal.

## Investigating a finding

Use the finding ID reported by the CLI:

```bash
python -m driftctl.cli.main explain CHANGE-0001
python -m driftctl.cli.main evidence CHANGE-0001
```

Replace the example ID with the actual finding ID. Review the observed change, evidence, detection time, and recommended action before deciding on severity or remediation.

## Practical triage checklist

1. Confirm the target and snapshot timestamps are correct.
2. Verify whether the change is expected from a deployment or configuration update.
3. For access-control changes, reproduce the behavior only within the authorized scope.
4. Compare the evidence from both snapshots and investigate relevant application logs or configuration.
5. Record the disposition and remediation so later reviews have context.

Treat snapshots, endpoint metadata, and findings as potentially sensitive. Store them securely and avoid committing real assessment data or credentials.