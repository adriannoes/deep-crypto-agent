## Summary

Consolidates all tool configurations and dependencies into `pyproject.toml`, following modern Python standards (PEP 518/621). Removes redundant configuration files and simplifies project dependency management.

## Main Changes

### Removed Files
- ❌ `requirements.txt` - Main dependencies consolidated into `pyproject.toml`
- ❌ `requirements-dev.txt` - Development dependencies consolidated into `pyproject.toml`
- ❌ `.mypy.ini` - Mypy configuration moved to `pyproject.toml`
- ❌ `.ruff.toml` - Ruff configuration moved to `pyproject.toml`

### Removed Dependencies
- ❌ `black` - Replaced by `ruff format` (faster and integrated)
- ❌ `isort` - Replaced by `ruff` with rule `I` (integrated isort)

### Modified Files
- ✏️ `pyproject.toml` - Consolidates all configurations:
  - Main and development dependencies
  - Pytest configuration
  - Ruff configuration (linting, formatting, and isort)
  - Mypy configuration (with overrides for specific modules)
- ✏️ `Dockerfile` - Updated to use `pip install -e ".[dev]"`
- ✏️ `Makefile` - Updated installation commands
- ✏️ `README.md` - Updated installation instructions
- ✏️ `docs/CONTRIBUTING.md` - Updated guide
- ✏️ `docs/DEVELOPMENT.md` - Updated instructions
- ✏️ `docs/DOCKER.md` - Updated references

## Commits

- `chore: remove redundant config files`
- `chore: consolidate tool configurations in pyproject.toml`
- `docs: update installation instructions to use pyproject.toml`
- `chore: update build files to use pyproject.toml`

## Checklist

- [x] Redundant files removed
- [x] Configurations consolidated in pyproject.toml
- [x] Documentation updated
- [x] Dockerfile and Makefile updated
- [x] Atomic commits following Conventional Commits
- [x] Pre-commit hooks passing

Co-authored-by: Adrianno Esnarriaga <esadrianno@gmail.com>
