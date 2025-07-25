import re
from typing import Dict, Any

DTC_BLOCK_PATTERN = re.compile(r"DTC_Code: (.+?)\n(.*?)\n\*{10,}", re.DOTALL)


def parse_dtc_txt(txt_path: str) -> Dict[str, Any]:
    """
    Parse the DTC .txt file and return a dict indexed by DTC code.
    """
    with open(txt_path, 'r', encoding='utf-8') as f:
        content = f.read()
    dtc_index = {}
    for match in DTC_BLOCK_PATTERN.finditer(content):
        dtc_code_line = match.group(1).strip()
        block = match.group(2).strip()
        # Extract just the DTC code (e.g., B1087, B155A-01, etc.)
        dtc_code = dtc_code_line.split()[0]
        dtc_index[dtc_code] = {
            'dtc_code_line': dtc_code_line,
            'block': block,
            'full_block': f"DTC_Code: {dtc_code_line}\n{block}"
        }
    return dtc_index 