"""Tests for the Fidelity report generator."""

import tempfile
from argparse import Namespace
from pathlib import Path
from unittest.mock import patch

from fidelity.fidelity import Fidelity
from fidelity.reader import HistoryRecord

# Fidelity CSV header (split for line length)
CSV_HEADER = (
    "Run Date,Action,Symbol,Description,Type,Quantity,Price,"
    "Commission,Fees,Accrued Interest,Amount,Cash Balance,Settlement Date"
)


def make_options(no_exclude: bool = False) -> Namespace:
    """Create a mock options namespace."""
    return Namespace(no_exclude=no_exclude)


def make_record(
    symbol: str,
    action: str = "BUY",
    quantity: float = 10.0,
    amount: float = -1000.0,
    run_date: str = "01/15/2024",
) -> HistoryRecord:
    """Create a test HistoryRecord with string values (as CSV reader does)."""
    # Pass strings to match CSV reader behavior; HistoryRecord converts them
    return HistoryRecord(
        run_date=run_date,
        action=action,
        symbol=symbol,
        description=f"{symbol} Description",
        type="Cash",
        quantity=str(quantity),  # type: ignore[arg-type]
        price="100.00",  # type: ignore[arg-type]
        commission="0",  # type: ignore[arg-type]
        fees="0",  # type: ignore[arg-type]
        accrued_interest="0",  # type: ignore[arg-type]
        amount=str(amount),  # type: ignore[arg-type]
        cash_balance="5000.00",  # type: ignore[arg-type]
        settlement_date="01/17/2024",
    )


class TestFidelityFiltering:
    """Tests for record filtering."""

    def test_excludes_spaxx_by_default(self) -> None:
        fidelity = Fidelity(make_options(no_exclude=False))
        fidelity.records = [
            make_record("AAPL"),
            make_record("SPAXX"),
            make_record("MSFT"),
        ]

        filtered = fidelity._get_history_records()

        assert len(filtered) == 2
        symbols = [r.symbol for r in filtered]
        assert "SPAXX" not in symbols
        assert "AAPL" in symbols
        assert "MSFT" in symbols

    def test_includes_spaxx_with_no_exclude(self) -> None:
        fidelity = Fidelity(make_options(no_exclude=True))
        fidelity.records = [
            make_record("AAPL"),
            make_record("SPAXX"),
            make_record("MSFT"),
        ]

        filtered = fidelity._get_history_records()

        assert len(filtered) == 3
        symbols = [r.symbol for r in filtered]
        assert "SPAXX" in symbols


class TestFidelityReadFiles:
    """Tests for reading input files."""

    def test_reads_multiple_files(self) -> None:
        csv_content = f"""\
Brokerage Account
Account: X12345678
{CSV_HEADER}
01/15/2024, BUY, AAPL, APPLE INC,Cash,10,150.00,0,0,0,-1500.00,8500.00,01/17/2024
"""
        files: list[Path] = []
        try:
            for _ in range(2):
                with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
                    f.write(csv_content)
                    f.flush()
                    files.append(Path(f.name))

            fidelity = Fidelity(make_options())
            fidelity.read_input_files([str(p) for p in files])

            assert len(fidelity.records) == 2
        finally:
            for p in files:
                p.unlink()

    def test_handles_empty_file_list(self) -> None:
        fidelity = Fidelity(make_options())
        fidelity.read_input_files([])
        assert len(fidelity.records) == 0


class TestFidelityReports:
    """Tests for report generation."""

    def test_history_report_runs_without_error(self) -> None:
        fidelity = Fidelity(make_options())
        fidelity.records = [
            make_record("AAPL", run_date="01/15/2024"),
            make_record("MSFT", run_date="01/16/2024"),
        ]

        with patch("rich.print"):
            fidelity.print_history_report()

    def test_symbol_report_runs_without_error(self) -> None:
        fidelity = Fidelity(make_options())
        fidelity.records = [
            make_record("AAPL"),
            make_record("AAPL", action="SELL", amount=1100.0),
            make_record("MSFT"),
        ]

        with patch("rich.print"):
            fidelity.print_symbol_report()

    def test_position_report_runs_without_error(self) -> None:
        fidelity = Fidelity(make_options())
        fidelity.records = [
            make_record("AAPL", quantity=10, amount=-1000),
            make_record("AAPL", quantity=5, amount=-500),
            make_record("MSFT", quantity=20, amount=-2000),
        ]

        with patch("rich.print"):
            fidelity.print_position_report()

    def test_reports_handle_empty_records(self) -> None:
        fidelity = Fidelity(make_options())
        fidelity.records = []

        with patch("rich.print"):
            fidelity.print_history_report()
            fidelity.print_symbol_report()
            fidelity.print_position_report()
