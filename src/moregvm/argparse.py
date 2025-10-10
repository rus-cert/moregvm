import re


def separated_list(s: str) -> list[str]:
    """custom type for argparse: list that can be comma or space separated"""
    return re.split("(?:,|\\s)+", s)
