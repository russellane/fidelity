"""Report generation for Fidelity transaction history."""

from argparse import Namespace
from collections import defaultdict
from enum import Enum

import rich
from rich.box import ROUNDED
from rich.table import Column, Table

from fidelity.reader import HistoryRecord, read_history_file

__all__ = ["Fidelity"]


class Style(Enum):
    """Styles for different table items."""

    TABLE = "#d06b64 italic"
    HEADER = "#92e1c0 italic"
    DETAIL = "#9a9cff"


def _get_report_table(title: str) -> Table:
    """Create a Rich table for report output."""

    return Table(
        Column("Run Date"),
        Column("Action"),
        Column("Symbol"),
        Column("Quantity", justify="right"),
        Column("Price", justify="right"),
        Column("Amount", justify="right"),
        Column("Balance", justify="right"),
        title=title,
        title_style=Style.TABLE.value,
        box=ROUNDED,
        style=Style.TABLE.value,
        header_style=Style.HEADER.value,
        row_styles=[Style.DETAIL.value],
    )


def _get_report_detail(rec: HistoryRecord, balance: float) -> list[str]:
    """Format a record as a table row."""

    return [
        rec.run_date,
        rec.action.lower(),
        rec.symbol,
        f"{rec.quantity:,.3f}",
        f"{rec.price:,.3f}",
        f"{rec.amount:,.3f}",
        f"{balance:,.3f}",
    ]


class Fidelity:
    """Report generator for Fidelity transaction history."""

    options: Namespace
    records: list[HistoryRecord]

    def __init__(self, options: Namespace) -> None:
        """Initialize with CLI options."""

        self.options = options
        self.records = []

    def read_input_files(self, files: list[str]) -> None:
        """Read transaction records from CSV files."""

        for filename in files:
            self.records.extend(read_history_file(filename))

    def print_history_report(self) -> None:
        """Print history report sorted by date."""

        table = _get_report_table("History Report")
        records = self._get_history_records()
        balance = 0.0

        for rec in sorted(records, key=lambda x: (x.t_run_date, x.symbol)):
            balance += rec.amount
            table.add_row(*_get_report_detail(rec, balance))

        rich.print(table)

    def print_symbol_report(self) -> None:
        """Print report grouped by symbol."""

        table = _get_report_table("Symbol Report")
        records = self._get_history_records()
        last_symbol = None
        balance = 0.0

        for rec in sorted(records, key=lambda x: (x.symbol, x.t_run_date)):
            if last_symbol is not None and last_symbol != rec.symbol:
                balance = 0.0
                table.add_section()
            last_symbol = rec.symbol
            balance += rec.amount
            table.add_row(*_get_report_detail(rec, balance))

        rich.print(table)

    def print_position_report(self) -> None:
        """Print position summary with totals per symbol."""

        symbols: dict[str, dict[str, float]] = defaultdict(
            lambda: {  # key=symbol
                "quantity": 0.0,
                "amount": 0.0,
                "balance": 0.0,
            }
        )

        balance = 0.0
        for rec in sorted(self.records, key=lambda x: x.symbol):
            symbols[rec.symbol]["quantity"] += rec.quantity
            symbols[rec.symbol]["amount"] += rec.amount
            balance += rec.amount
            symbols[rec.symbol]["balance"] = balance

        table = Table(
            Column("Symbol"),
            Column("Quantity", justify="right"),
            Column("Amount", justify="right"),
            Column("Balance", justify="right"),
            title="Position Report",
            title_style=Style.TABLE.value,
            box=ROUNDED,
            style=Style.TABLE.value,
            header_style=Style.HEADER.value,
            row_styles=[Style.DETAIL.value],
        )

        for symbol, data in symbols.items():
            table.add_row(
                symbol,
                f"{data['quantity']:,.3f}",
                f"{data['amount']:,.3f}",
                f"{data['balance']:,.3f}",
            )

        rich.print(table)

    def _get_history_records(self) -> list[HistoryRecord]:
        """Return records, optionally filtering out SPAXX."""

        if self.options.no_exclude:
            return self.records

        records = [x for x in self.records if x.symbol not in ["SPAXX"]]
        return records
