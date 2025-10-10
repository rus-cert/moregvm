"""
Progress indicators
"""

import sys

VT100_SAVECURSOR = "\x1B7"
VT100_RESTORECURSOR = "\x1B8"
VT100_CLEAREOS = "\x1B[J"


def progress_indicator(
    current: object,
    maximum: object,
    *,
    name: str = "greenbone",
) -> None:
    maximum = "connecting" if maximum is None else maximum
    print(f'{VT100_CLEAREOS}{VT100_SAVECURSOR}...{name} {current}/{maximum}...{VT100_RESTORECURSOR}', end='', file=sys.stderr, flush=True)


def progress_indicator_erase() -> None:
    print(VT100_CLEAREOS, end="", file=sys.stderr, flush=True)
