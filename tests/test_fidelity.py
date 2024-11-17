import sys

from fidelity.cli import FidelityCLI


def run_cli(options: list[str]) -> None:
    """Test calling the cli directly."""

    sys.argv = ["fidelity"]
    if options:
        sys.argv += options
    print(f"\nRunning {sys.argv!r}", flush=True)
    FidelityCLI().main()


def test_file_dev_null() -> None:
    run_cli(["/dev/null"])


def test_use_datafiles() -> None:
    run_cli(["--use-datafiles"])
