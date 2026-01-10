# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Build and Development Commands

This project uses PDM for dependency management.

```bash
# Install dependencies
pdm install

# Run the CLI
pdm run fidelity [options] [FILES...]

# Run tests
pdm run pytest tests/

# Run a single test
pdm run pytest tests/test_cli.py::test_version

# Linting and formatting
pdm run black .
pdm run isort .
pdm run flake8
pdm run mypy .
```

## Code Style

- Line length: 97 characters (configured for black, isort, pylint)
- Type hints: strict mypy enabled
- Docstrings: Google convention (pydocstyle)

## Architecture

This is a CLI tool for processing Fidelity brokerage transaction history CSV files.

**Key modules:**
- `fidelity/cli.py` - CLI entry point using `libcli.BaseCLI`. Handles argument parsing and orchestrates report generation.
- `fidelity/fidelity.py` - Core business logic. Contains `Fidelity` class for reading CSV files and `HistoryRecord` dataclass for transaction data. Generates three reports: History, Symbol, and Position.

**Configuration:** Default config file at `~/.fidelity.toml` with `datafiles` key pointing to CSV files.

**External dependency:** Uses `rlane-libcli` for CLI infrastructure (argument parsing, config file handling).
