import json
import logging
from typing import List

import requests

from .file_reader import append_to_markdown_file

logger = logging.getLogger(__name__)


def make_http_request(request_type: str, url: str):
    try:
        with requests.request(
            request_type,
            url,
            headers={"Content-Type": "application/json"},
        ) as response:
            return response
    except Exception as e:
        logger.error(f"Error making http request to {url}: {e}")


def count_phases(trials) -> None:
    """Counts trials in each phase and writes results to markdown.
    Focuses on Phase 1, 2, and 3 for the final output.
    Logs detailed phase information and creates formatted report."""
    phases = count_elements(trials, 'phase')
    logger.debug(f"Result of phase count: {phases}")

    print_phases(phases)


def print_phases(phases: dict):
    """Creates formatted markdown report of phase distribution.
    Focuses on Phase 1, 2, and 3 trials with counts and percentages.
    Logs phase information and writes to assignment results file."""
    logger.info("Number of times phases occurred:")

    markdown_content = "## Assignment 1\n\n"
    markdown_content += "### How many Phase 1, 2 and 3 trials are there?\n\n"

    # Add results to markdown, only for phases 1, 2, and 3
    markdown_content += "Number of times phases occurred:\n\n"
    for phase, count in phases.items():
        if phase in ['Phase 1', 'Phase 2', 'Phase 3']:
            markdown_content += f"- {phase}: {count}\n"
    markdown_content += "\n"

    # Write to markdown file
    append_to_markdown_file(markdown_content)

    # Also log the information
    for phase, count in phases.items():
        logger.info(f"{phase}: {count}")


def count_elements(trials, element: str):
    element_dict = {}
    for trial in trials:
        if trial[element] is None:
            continue
        for e in trial[element]:
            if e not in element_dict:
                element_dict[e] = 0
            element_dict[e] += 1
    return element_dict


def sorted_counts(d: dict) -> List[tuple]:
    return dict(sorted(d.items(), key=lambda x: x[1], reverse=True))


def print_conditions(elements: dict, limit: int = None):
    """Formats and writes top conditions analysis to markdown file.
    Creates numbered list of most common conditions with counts.
    Limits output to specified number (default 10) for readability."""
    markdown_content = "## Assignment 3\n\n"
    markdown_content += "### What are the top 10 most commonly studied conditions?\n\n"

    markdown_content += "Top 10 Conditions:\n\n"
    if limit is None:
        limit = len(elements)
    for i, (element, count) in enumerate(elements.items()):
        if i >= limit:
            break
        markdown_content += f"{i + 1}. {element}: {count}\n"

    append_to_markdown_file(markdown_content)
    logger.info("Calculated the top 10 conditions.")


def analyze_conditions(trials):

    conditions = sorted_counts(count_elements(trials, 'conditions'))    
    print_conditions(conditions, 10)


def get_ten_sample_trials(trials: List[dict], phase: str) -> List[dict]:
    trial_subset = [trial for trial in trials if trial.get('phase') and phase in trial['phase']][:10]
    logger.debug(f"Found {len(trial_subset)} trials in phase {phase}.")
    return trial_subset


def calculate_average_number_of_enrollments(trials):
    """Calculates average enrollments for Phase 1, 2, and 3 trials.
    Makes API calls to clinicaltrials.gov to get enrollment data.
    Uses sample of 10 trials per phase and writes results to markdown."""

    markdown_content = "## Assignment 2\n\n"
    markdown_content += (
        "### What is the average amount of (Estimated) Enrollments in a clinical trial "
        "in Phase 1, 2 and 3 each?\n\n"
    )

    markdown_content += "Average number of enrollments:\n"
    for phase in ['Phase 1', 'Phase 2', 'Phase 3']:
        logger.info(f"Calculating the average number of enrollments for phase {phase}.")
        avg = calculate_average_number_of_enrollments_per_phase(trials, phase, 10)

        markdown_content += f" - {phase}: {avg}\n"

    # Write to markdown file
    append_to_markdown_file(markdown_content)


def calculate_average_number_of_enrollments_per_phase(
    trials: List[dict],
    phase: str,
    number_of_studies: int
) -> float:
    """Calculates average enrollment for specific phase using API calls.
    Fetches enrollment data from clinicaltrials.gov for sample trials.
    Returns average enrollment count for the specified phase."""

    average_number_of_enrollments = 0
    trials_in_specified_phase = get_ten_sample_trials(trials, phase)

    for trial in trials_in_specified_phase:
        trial_id = trial['utn']
        url = f"https://clinicaltrials.gov/api/v2/studies?query.id={trial_id}"
        logger.debug(f"Making HTTP request to {url}...")
        trial_test = make_http_request("GET", url)
        trial_dict = json.loads(trial_test.text)
        number_of_enrollments = trial_dict["studies"][0]["protocolSection"]\
            ["designModule"]["enrollmentInfo"]["count"]

        logger.debug(
            f"trial {trial_id} in {phase} has {number_of_enrollments} enrollments"
        )
        average_number_of_enrollments += number_of_enrollments

    return (
        average_number_of_enrollments / number_of_studies
        if number_of_studies > 0 else 0
    )
