"""Column metadata for data grids."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class ColMd:
    """Column metadata for AG Grid formatting.

    Args:
        name: Column name (must match DataFrame column)
        label: Display label (defaults to title-cased name)
        format: Format type - 'default', 'perc', 'percent', 'perc_div', 'dec', 'mag_si'
        pinned: Pin column to left side
        hidden: Hide column
        precision: Decimal precision (overrides default)
    """

    name: str
    label: Optional[str] = None
    format: str = "default"  # percent, decimal, mag_si (convert to K/M/G suffixes)
    pinned: bool = False
    hidden: bool = False
    precision: Optional[int] = None

    def __post_init__(self):
        if not isinstance(self.name, str):
            self.name = str(self.name)
        if self.label is None:
            self.label = self.name.title().replace("_", " ")
