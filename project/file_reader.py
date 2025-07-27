import json
import logging
import os
from typing import List

from pandas import DataFrame, read_csv

logger = logging.getLogger(__name__)


def read_payloads_jsonl(filename) -> List[dict]:
    """
    Reads JSONL file line by line, parses JSON objects, returns trial data.
    Shows progress every 1000 lines and handles parsing errors gracefully.
    Returns empty list if file not found or on critical errors.
    """
    trials = []
    if not os.path.exists(filename):
        logger.error(f"File '{filename}' not found.")
        return []

    with open(filename, 'r', encoding='utf-8') as file:
        for line_num, line in enumerate(file, 1):
            line = line.strip()
            if not line:
                continue

            try:
                trials.append(json.loads(line))

                # Show progress every 1000 lines
                if line_num % 1000 == 0:
                    logger.info(f"Processed {line_num} lines...")

            except json.JSONDecodeError as e:
                logger.warning(f"Invalid JSON on line {line_num}: {e}")

        logger.info(f"Loaded {len(trials)} trials from {line_num} lines")   
    return trials


def read_indexing_records(file_path: str) -> DataFrame:
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File '{file_path}' not found.")

    df = read_csv(file_path)
    return df


def initialize_markdown_file(file_path: str = "data/assignment_results.md"):
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write("# Assignment Results\n\n")


def append_to_markdown_file(content: str):
    file_path = "data/assignment_results.md"
    with open(file_path, 'a', encoding='utf-8') as f:
        f.write(content)
