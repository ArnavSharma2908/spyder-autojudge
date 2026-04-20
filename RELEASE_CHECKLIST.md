# Release Checklist

## Before release

1. Update version in:
   - `pyproject.toml`
   - `spyder_autojudge/__init__.py`
2. Update `CHANGELOG.md`.
3. Build and verify package:

```bash
python -m pip install -U build twine
python -m build
python -m twine check dist/*
```

4. Test install locally:

```bash
python -m pip install dist/spyder_autojudge-<version>-py3-none-any.whl
```

## Publish

1. Upload to TestPyPI:

```bash
python -m twine upload --repository testpypi dist/*
```

2. Upload to PyPI:

```bash
python -m twine upload dist/*
```

3. Create GitHub release with matching tag (`vX.Y.Z`).
