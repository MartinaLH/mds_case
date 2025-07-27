import logging
import os
import json
from typing import List
from pandas import read_csv, DataFrame

# Create logger for file_reader module
logger = logging.getLogger("file_reader")


def read_payloads_jsonl(filename) -> List[dict]:
    """
    Read the payloads.jsonl file line by line and process each JSON object

    Args:
        filename (str): Path to the JSONL file

    Returns:
        List[dict]: List of trial dictionaries
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
    """
    Create or reset the assignment_results.md file in the data folder.
    If the file exists, it will be emptied and recreated with the header.
    """
    # Create or overwrite the file with the header
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write("# Assignment Results\n\n")


def append_to_markdown_file(content: str):
    """
    Append content to the assignment_results.md file in the data folder.

    Args:
        content (str): The content to append to the file
    """
    file_path = "data/assignment_results.md"

    # Append content to the file
    with open(file_path, 'a', encoding='utf-8') as f:
        f.write(content)
