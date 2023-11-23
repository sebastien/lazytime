from typing import NamedTuple

TLiteral = bool | int | float | str
TPrimitive = TLiteral | list[TLiteral] | dict[str, TLiteral]


class Entry(NamedTuple):
    id: int
    time: float
    timezone: str
    action: str
    value: int | float | bool | None
    data: TPrimitive | None


class Journal:
    entries: list[Entry]


# EOF
