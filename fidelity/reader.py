"""CSV reader for Fidelity transaction history files."""

import csv
from dataclasses import dataclass, field, fields
from time import mktime, strptime

__all__ = ["HistoryRecord", "read_history_file"]


@dataclass
class HistoryRecord:
    """A single transaction record from Fidelity history export."""

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
        """Clean and convert field values."""

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


def read_history_file(filename: str) -> list[HistoryRecord]:
    """Read a Fidelity history CSV file and return transaction records.

    Fidelity CSV files have 3 header lines before the data rows.
    """

    records: list[HistoryRecord] = []
    with open(filename, encoding="utf-8") as fp:
        # Skip 3 header lines (Fidelity CSV format)
        _ = fp.readline()
        _ = fp.readline()
        _ = fp.readline()
        csv_reader = csv.reader(fp)
        for row in csv_reader:
            if not row:
                break
            rec = HistoryRecord(*row)  # type: ignore[arg-type]
            records.append(rec)
    return records
