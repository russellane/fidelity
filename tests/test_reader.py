"""Tests for the reader module."""

import tempfile
from pathlib import Path
from typing import Any

from fidelity.reader import HistoryRecord, read_history_file

# Fidelity CSV header (split for line length)
CSV_HEADER = (
    "Run Date,Action,Symbol,Description,Type,Quantity,Price,"
    "Commission,Fees,Accrued Interest,Amount,Cash Balance,Settlement Date"
)


def make_record(**kwargs: Any) -> HistoryRecord:
    """Create a HistoryRecord from string values (as CSV reader does)."""
    defaults: dict[str, str] = {
        "run_date": "01/15/2024",
        "action": "BUY",
        "symbol": "AAPL",
        "description": "Apple Inc",
        "type": "Cash",
        "quantity": "10",
        "price": "150.00",
        "commission": "0",
        "fees": "0",
        "accrued_interest": "0",
        "amount": "-1500.00",
        "cash_balance": "5000.00",
        "settlement_date": "01/17/2024",
    }
    defaults.update(kwargs)
    return HistoryRecord(**defaults)  # type: ignore[arg-type]


class TestHistoryRecord:
    """Tests for HistoryRecord dataclass."""

    def test_strips_whitespace_from_strings(self) -> None:
        rec = make_record(
            run_date=" 01/15/2024 ",
            action=" BUY ",
            symbol=" AAPL ",
            description=" Apple Inc ",
        )
        assert rec.run_date == "01/15/2024"
        assert rec.action == "BUY"
        assert rec.symbol == "AAPL"
        assert rec.description == "Apple Inc"

    def test_converts_strings_to_floats(self) -> None:
        rec = make_record(
            quantity="10.5",
            price="150.25",
            commission="4.95",
            fees="0.02",
        )
        assert rec.quantity == 10.5
        assert rec.price == 150.25
        assert rec.commission == 4.95
        assert rec.fees == 0.02

    def test_handles_empty_float_values(self) -> None:
        rec = make_record(
            action="DIVIDEND",
            quantity="",
            price="",
            commission="",
        )
        assert rec.quantity == 0.0
        assert rec.price == 0.0
        assert rec.commission == 0.0

    def test_parses_run_date_to_timestamp(self) -> None:
        rec = make_record(
            run_date="01/15/2024",
            settlement_date="01/17/2024",
        )
        assert rec.t_run_date > 0
        assert rec.t_settlement_date > 0
        assert rec.t_settlement_date > rec.t_run_date

    def test_handles_empty_dates(self) -> None:
        rec = make_record(
            run_date="",
            action="PENDING",
            settlement_date="",
        )
        assert rec.t_run_date == 0
        assert rec.t_settlement_date == 0


class TestReadHistoryFile:
    """Tests for read_history_file function."""

    def test_reads_csv_file(self) -> None:
        csv_content = f"""\
Brokerage Account
Account: X12345678
{CSV_HEADER}
01/15/2024, BUY, AAPL, APPLE INC,Cash,10,150.00,0,0.02,0,-1500.02,8499.98,01/17/2024
01/16/2024, SELL, MSFT, MICROSOFT,Cash,5,400.00,0,0.01,0,1999.99,10499.97,01/18/2024
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write(csv_content)
            f.flush()
            temp_path = Path(f.name)

        try:
            records = read_history_file(str(temp_path))
            assert len(records) == 2

            assert records[0].symbol == "AAPL"
            assert records[0].action == "BUY"
            assert records[0].quantity == 10.0
            assert records[0].price == 150.00

            assert records[1].symbol == "MSFT"
            assert records[1].action == "SELL"
            assert records[1].quantity == 5.0
        finally:
            temp_path.unlink()

    def test_stops_at_empty_row(self) -> None:
        csv_content = f"""\
Brokerage Account
Account: X12345678
{CSV_HEADER}
01/15/2024, BUY, AAPL, APPLE INC,Cash,10,150.00,0,0,0,-1500.00,8500.00,01/17/2024

01/16/2024, SELL, MSFT, MICROSOFT,Cash,5,400.00,0,0,0,2000.00,10500.00,01/18/2024
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write(csv_content)
            f.flush()
            temp_path = Path(f.name)

        try:
            records = read_history_file(str(temp_path))
            assert len(records) == 1
            assert records[0].symbol == "AAPL"
        finally:
            temp_path.unlink()

    def test_reads_empty_file_after_headers(self) -> None:
        csv_content = f"""\
Brokerage Account
Account: X12345678
{CSV_HEADER}
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write(csv_content)
            f.flush()
            temp_path = Path(f.name)

        try:
            records = read_history_file(str(temp_path))
            assert len(records) == 0
        finally:
            temp_path.unlink()
