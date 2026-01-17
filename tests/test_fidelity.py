import sys

from fidelity.cli import main


def run_cli(options: list[str]) -> None:
    """Test calling the cli directly."""

    sys.argv = ["fidelity"]
    if options:
        sys.argv += options
    print(f"\nRunning {sys.argv!r}", flush=True)
    main()


def test_file_dev_null() -> None:
    run_cli(["/dev/null"])


def test_use_datafiles() -> None:
    run_cli(["--use-datafiles"])


def test_use_datafiles_no_exclude() -> None:
    run_cli(["--use-datafiles", "--no-exclude"])
