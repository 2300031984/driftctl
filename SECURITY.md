# Security Policy

## Intended use

DriftCTL is intended for defensive attack-surface monitoring in local labs, systems you own, and assessments for which you have explicit authorization. You are responsible for confirming that your testing is within the target's approved scope and rules.

## Safe testing practices

- Prefer an isolated local lab for development and regression testing.
- Start with low request rates and avoid unnecessary load on target services.
- Do not attempt to bypass access controls, modify production data, or test out-of-scope assets unless the written authorization explicitly permits it.
- Treat collected endpoint metadata, snapshots, and findings as potentially sensitive. Store them securely and remove data that is no longer needed.
- Never commit API keys, cookies, session tokens, credentials, or private assessment data to the repository.

## Reporting a vulnerability

If you discover a security issue in DriftCTL itself, report it privately to the repository maintainer through a private contact method listed on the maintainer's GitHub profile. Include:

1. A concise description of the issue and its impact.
2. The affected version or commit, if known.
3. Reproduction steps using a local or otherwise authorized environment.
4. Any suggested mitigation, if available.

Please avoid publishing exploit details before the maintainer has had a reasonable opportunity to investigate and address the issue. Do not include secrets or third-party personal data in a report.

## Scope

This policy concerns vulnerabilities in DriftCTL and its repository. It does not grant permission to test any third-party system.