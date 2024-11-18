"""Docstring."""

import csv
from collections import defaultdict
from dataclasses import dataclass, field, fields
from enum import Enum
from time import mktime, strptime

import rich
from rich.box import ROUNDED
from rich.table import Column, Table

__all__ = ["Fidelity"]


class Style(Enum):
    """Styles for different table items."""

    TABLE = "#d06b64 italic"
    HEADER = "#92e1c0 italic"
    DETAIL = "#9a9cff"


@dataclass
class HistoryRecord:
    """Docstring."""

    # pylint: disable=too-many-instance-attributes

    run_date: str
    action: str
    symbol: str
    description: str
    type: str
    quantity: float
    price: float
    commission: float
    fees: float
    accrued_interest: float
    amount: float
    cash_balance: float
    settlement_date: str

    t_run_date: int = field(init=False)
    t_settlement_date: int = field(init=False)

    def __post_init__(self) -> None:
        """Docstring."""

        # Strings have a leading blank.
        self.run_date = self.run_date.strip()
        self.action = self.action.strip()
        self.symbol = self.symbol.strip()
        self.description = self.description.strip()

        # Convert strings to floats.
        for f in fields(self):
            if f.type == float:
                value = getattr(self, f.name)
                if isinstance(value, str):
                    try:
                        value = float(value)
                    except ValueError:
                        value = 0.0
                    setattr(self, f.name, value)

        # Convert date-strings to unix time integer.
        self.t_run_date = (
            int(mktime(strptime(self.run_date, "%m/%d/%Y"))) if self.run_date else 0
        )

        self.t_settlement_date = (
            int(mktime(strptime(self.settlement_date, "%m/%d/%Y")))
            if self.settlement_date
            else 0
        )

    @staticmethod
    def get_report_table(title: str) -> Table:
        """Docstring."""

        return Table(
            Column("Run Date"),
            Column("Action"),
            Column("Symbol"),
            Column("Quantity", justify="right"),
            Column("Price", justify="right"),
            Column("Amount", justify="right"),
            title=title,
            title_style=Style.TABLE.value,
            box=ROUNDED,
            style=Style.TABLE.value,
            header_style=Style.HEADER.value,
            row_styles=[Style.DETAIL.value],
        )

    def get_report_detail(self) -> list[str]:
        """Docstring."""

        return [
            f"{self.run_date}",
            f"{self.action.lower()}",
            f"{self.symbol}",
            f"{self.quantity:,.3f}",
            f"{self.price:,.3f}",
            f"{self.amount:,.3f}",
        ]


class Fidelity:
    """Docstring."""

    records: list[HistoryRecord] = []

    def read_input_files(self, files: list[str]) -> None:
        """Docstring."""

        for filename in files:
            with open(filename, encoding="utf-8") as fp:
                _ = fp.readline()
                _ = fp.readline()
                _ = fp.readline()
                csv_reader = csv.reader(fp)
                for row in csv_reader:
                    if not row:
                        break
                    rec = HistoryRecord(*row)  # type: ignore[arg-type]
                    self.records.append(rec)

    def print_history_report(self) -> None:
        """Print Report."""

        excludes = ["SPAXX"]
        if excludes:
            records = [x for x in self.records if x.symbol not in excludes]
        else:
            records = self.records

        table = HistoryRecord.get_report_table("History Report")

        for rec in sorted(records, key=lambda x: (x.t_run_date, x.symbol)):
            table.add_row(*rec.get_report_detail())

        rich.print(table)

    def print_symbol_report(self) -> None:
        """Print Report."""

        excludes = ["SPAXX"]
        if excludes:
            records = [x for x in self.records if x.symbol not in excludes]
        else:
            records = self.records

        table = HistoryRecord.get_report_table("Symbol Report")

        last_symbol = None
        for rec in sorted(records, key=lambda x: (x.symbol, x.t_run_date)):
            if last_symbol is not None and last_symbol != rec.symbol:
                table.add_section()
            last_symbol = rec.symbol
            table.add_row(*rec.get_report_detail())

        rich.print(table)

    def print_position_report(self) -> None:
        """Print Report."""

        symbols: dict[str, dict[str, float]] = defaultdict(
            lambda: {  # key=symbol
                "quantity": 0.0,
                "amount": 0.0,
            }
        )

        for rec in self.records:
            symbols[rec.symbol]["quantity"] += rec.quantity
            symbols[rec.symbol]["amount"] += rec.amount

        table = Table(
            Column("Symbol"),
            Column("Quantity", justify="right"),
            Column("Amount", justify="right"),
            title="Position Report",
            title_style=Style.TABLE.value,
            box=ROUNDED,
            style=Style.TABLE.value,
            header_style=Style.HEADER.value,
            row_styles=[Style.DETAIL.value],
        )

        for symbol, data in symbols.items():
            table.add_row(symbol, f"{data['quantity']:,.3f}", f"{data['amount']:,.3f}")

        rich.print(table)
