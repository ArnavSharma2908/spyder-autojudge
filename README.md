# Spyder AutoJudge

Spyder AutoJudge is a Spyder plugin that adds a dockable pane for running competitive-programming style test cases against the latest modified Python file in a target folder.

## Features

- Detects the latest modified `.py` file in a selected folder.
- Reads test inputs from `input.txt` and expected outputs from `expected.txt`.
- Runs each test case with timeout protection.
- Shows pass, wrong-answer, and runtime-error summary.
- Displays a result pie chart (when `matplotlib` is available).

## Prerequisites

- Python 3.9 or newer.
- Spyder 5.4 or newer.
- A Spyder environment where `spyder-autojudge` is installed.
- Optional but recommended: `matplotlib` for the pie chart visualization.

## Installation

Install from PyPI:

```bash
pip install spyder-autojudge
```

If you use virtual environments, install into the same environment used by Spyder.

Quick verification:

```bash
python -m pip show spyder-autojudge
```

If Spyder does not detect the plugin, restart Spyder after installation.

## Usage

1. Open Spyder.
2. Open the AutoJudge pane from Spyder's plugin UI.
3. Select your working folder from the pane options.
4. Add three files in that folder:
   - Your solution files (`*.py`).
   - `input.txt` containing test inputs.
   - `expected.txt` containing expected outputs.
5. Click `Run Latest`.

AutoJudge will select the most recently modified Python file and run it against each test case pair.

### Recommended working folder layout

```text
your-problem-folder/
  solution.py
  trial.py
  input.txt
  expected.txt
```

`Run Latest` will choose whichever Python file has the latest modified timestamp.

### Test case format

Use blank lines to separate test cases in both files. Test case count must match between `input.txt` and `expected.txt`.

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

### How `input.txt` is used

- Each block is passed to the program's stdin for one test case.
- Multi-line input is supported inside a block.
- Blocks are split on blank lines.

### How `expected.txt` is used

- Each block is the exact expected stdout for the corresponding input block.
- Output comparison is done per test case.
- The number of blocks must be equal to `input.txt`.

### Result statuses

- SUCCESS: Program output matches expected output.
- WRONG OUTPUT: Program ran but output did not match expected output.
- ERROR: Runtime error, timeout, or execution issue.

### Pie chart and summary panel

When `matplotlib` is available, AutoJudge renders a pie chart with:

- Success (green)
- Wrong (orange)
- Error (red)

If no test data is available yet, the chart area shows a placeholder message.

### Working screenshot

Add your screenshot to `docs/images/autojudge-working.png`, then this section will render automatically:

![Spyder AutoJudge working screenshot](docs/images/autojudge-working.png)

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
