# Spyder AutoJudge

Spyder AutoJudge is a Spyder plugin that adds a dockable pane for running competitive-programming style test cases against the latest modified Python file in a target folder.

## Features

- Detects the latest modified `.py` file in a selected folder.
- Reads test inputs from `input.txt` and expected outputs from `expected.txt`.
- Runs each test case with timeout protection.
- Shows pass, wrong-answer, and runtime-error summary.
- Displays a result pie chart (when `matplotlib` is available).

## Installation

```bash
pip install spyder-autojudge
```

## Usage

1. Open Spyder.
2. Enable the plugin from Spyder's plugin discovery (if required by your Spyder setup).
3. Open the AutoJudge pane.
4. Choose your working folder from the pane options.
5. Create test files in that folder:
   - `input.txt`
   - `expected.txt`
6. Click `Run Latest`.

### Test case format

Use blank lines to separate test cases in both files.

`input.txt` example:

```text
2
3

10
20
```

`expected.txt` example:

```text
5

30
```

## Development

```bash
python -m pip install -U build twine
python -m build
python -m twine check dist/*
```

## Publishing to PyPI

```bash
python -m twine upload dist/*
```

For first release, test on TestPyPI first:

```bash
python -m twine upload --repository testpypi dist/*
```

## License

MIT License. See [LICENSE](LICENSE).
