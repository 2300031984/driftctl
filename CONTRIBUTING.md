# Contributing to DriftCTL

Thank you for helping improve DriftCTL, a Python CLI for detecting meaningful changes in an application's externally observable attack surface.

## Before starting

1. Check existing issues and pull requests to avoid duplicating work.
2. For larger changes, open an issue to discuss the proposed behavior first.
3. Work only with systems you own or are explicitly authorized to assess.

## Development setup

Use Python 3.11 or newer.

```bash
git clone https://github.com/2300031984/driftctl.git
cd driftctl
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Make a change

- Keep changes focused and explain the problem they solve.
- Add or update tests for behavior changes, especially snapshot comparison, risk classification, and finding persistence.
- Avoid committing credentials, tokens, real target data, or generated snapshot artifacts.
- Prefer clear, descriptive names and small functions.

## Validate

Run the test suite before opening a pull request:

```bash
pytest -v
```

Include the test command and its actual result in your pull request description. Do not claim tests passed unless you ran them.

## Pull request checklist

- [ ] The change has a clear purpose and scope.
- [ ] Relevant tests were added or updated.
- [ ] Tests were run and results are reported accurately.
- [ ] Documentation and examples match the implementation.
- [ ] No secrets or unauthorized target data are included.

Describe the motivation, implementation, validation performed, and any known limitations in the pull request.