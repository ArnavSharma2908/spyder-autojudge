# Contributing to Spyder AutoJudge

Thanks for your interest in contributing.

## Development setup

1. Fork and clone the repository.
2. Create and activate a virtual environment.
3. Install dependencies:

```bash
python -m pip install -U pip
python -m pip install -e .
```

## Pull request process

1. Create a feature branch from `main`.
2. Make small, focused commits.
3. Update docs and changelog when behavior changes.
4. Ensure packaging still builds with:

```bash
python -m build
python -m twine check dist/*
```

5. Open a pull request with:
   - Clear summary
   - Screenshots if UI changed
   - Reproduction steps for bug fixes

## Reporting issues

When opening an issue, include:

- Spyder version
- Python version
- OS
- Steps to reproduce
- Expected behavior
- Actual behavior
