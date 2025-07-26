import json
import logging

from typing import List

import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("read_payloads")



def read_payloads_jsonl(filename) -> List[dict]:
    """
    Read the payloads.jsonl file line by line and process each JSON object

    Args:
        filename (str): Path to the JSONL file
    """
    try:
        trials: List[dict] = []

        with open(filename, 'r', encoding='utf-8') as file:
            line_count = 0
            for line in file:
                line_count += 1

                # Skip empty lines
                if not line.strip():
                    continue

                try:
                    # Parse JSON from each line
                    trials.append(json.loads(line))

                    # Show progress every 1000 lines
                    if line_count % 1000 == 0:
                        logger.info(f"Processed {line_count} lines...")

                except json.JSONDecodeError as e:
                    logger.error(f"Error parsing JSON on line {line_count}: {e}")
                    continue

            logger.info(f"\nFinished processing {line_count} lines total.")

        return trials
    except FileNotFoundError:
        logger.error(f"Error: File '{filename}' not found.")
    except Exception as e:
        logger.error(f"Error reading file: {e}")


def make_http_request(request_type: str, url: str):
    """
    Make an HTTP request to the specified URL with the given request type.
    Args:
        request_type (str): The type of HTTP request (e.g., 'GET', 'POST')
        url (str): The URL to make the request to

    Returns:
        Response object from the requests library
        """
    try:
        with requests.request(
            request_type,
            url,
            headers={"Content-Type": "application/json"},
        ) as response:
            return response
    except Exception as e:
        logger.error(f"Error making http request to {url}: {e}")

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

def print_phases(phases: dict):
    logger.info("Number of times phases occurred:")
    for phase, count in phases.items():
        print(f"{phase}: {count}")
    print("\n")

def element_printer(elements: dict, limit: int = None):
    if limit is None:
        limit = len(elements)
    for i, (element, count) in enumerate(elements.items()):
        if i >= limit:
            break
        print(f"{element}: {count}")


def get_ten_sample_trials(trials: List[dict], phase: str) -> List[dict]:
    trial_subset = [trial for trial in trials if trial.get('phase') and phase in trial['phase']][:10]
    logger.debug(f"Found {len(trial_subset)} trials in phase {phase}.")
    return trial_subset


def calculate_average_number_of_enrollments(trials):

    logger.info("\nAverage number of enrollments per phase:")
    for phase in ['Phase 1', 'Phase 2', 'Phase 3']:
        avg = calculate_average_number_of_enrollments_per_phase(trials, phase, 10)
        logger.info(f"Average number of enrollments for {phase}: {avg}")

def calculate_average_number_of_enrollments_per_phase(trials: List[dict], phase: str, number_of_studies: int) -> float:

    average_number_of_enrollments = 0
    trials_in_specified_phase = get_ten_sample_trials(trials, phase)

    for trial in trials_in_specified_phase:
        trial_id = trial['utn']
        url = f"https://clinicaltrials.gov/api/v2/studies?query.id={trial_id}"
        logger.debug(f"Making HTTP request to {url}...")
        trial_test = make_http_request("GET", url)
        trial_dict = json.loads(trial_test.text)
        number_of_enrollments =  trial_dict["studies"][0]["protocolSection"]["designModule"]["enrollmentInfo"]["count"]

        logger.debug(f"trial {trial_id} in {phase} has {number_of_enrollments} enrollments")
        average_number_of_enrollments += number_of_enrollments

    return average_number_of_enrollments / number_of_studies if number_of_studies > 0 else 0

if __name__ == "__main__":


    #Read the payloads.jsonl file
    trials = read_payloads_jsonl("data/payloads.jsonl")

    # Count the number of trials in each phase
    phases = count_elements(trials, 'phase')
    print_phases(phases)

    # Calculate the average number of enrollments for each phase for the first 10 trials
    calculate_average_number_of_enrollments(trials)


    conditions = sorted_counts(count_elements(trials, 'conditions'))

    logger.info(f"\nTop 10 Conditions:")
    element_printer(conditions, 10)










