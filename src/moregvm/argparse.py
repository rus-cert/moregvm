import re
from typing import List

def separated_list(s: str) -> List[str]:
    """custom type for argparse: list that can be comma or space separated"""
    return re.split('(?:,|\s)+', s)

