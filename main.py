#!/usr/bin/env python3
"""
Main entry point for the MDS case study.
Run this script from the mds_case directory.
"""

import logging
from project.file_reader import (
    initialize_markdown_file,
    read_indexing_records,
    read_payloads_jsonl,
)
from project.trial_analyzer import (
    analyze_conditions,
    count_phases,
    calculate_average_number_of_enrollments,
)
from project.trial_researcher import (
    analyze_eligibility_criteria,
    determine_eligibility_per_trial,
    initiate_openai_client,
)

INDEXING_RECORDS_PATH = "data/indexing_records.csv"
TRIAL_INFORMATION_PATH = "data/payloads.jsonl"
PATIENT_01_PATH = "data/patient_01.json"
PATIENT_02_PATH = "data/patient_02.json"
PATIENT_03_PATH = "data/patient_03.json"
ASSIGNMENT_RESULTS_PATH = "data/assignment_results.md"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__.split('.')[-1])


def initialize_assignment() -> tuple:

    initialize_markdown_file()
    trial_list = read_payloads_jsonl(TRIAL_INFORMATION_PATH)
    indexing_records = read_indexing_records(INDEXING_RECORDS_PATH)
    patient_paths = [PATIENT_01_PATH, PATIENT_02_PATH, PATIENT_03_PATH]
    client = initiate_openai_client()

    return trial_list, indexing_records, patient_paths, client


def main():
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("main")

    logger.info("Starting MDS case study analysis...")

    # Initialize and load trial data
    trials, indexing_records, patient_paths, client = initialize_assignment()

    # Assignment 1: Count the number of trials in each phase
    logger.info("Counting the number of trials in each phase.")
    count_phases(trials)

    # Assignment 2: What is the average amount of (Estimated) Enrollments
    # in a clinical trial in Phase 1, 2 and 3 each?
    logger.info("Calculating the average number of enrollments for each phase.")
    calculate_average_number_of_enrollments(trials)

    # Assignment 3: What are the top 10 most commonly studied conditions?
    logger.info("Calculating the top 10 most commonly studied conditions.")
    analyze_conditions(trials)

    # Assignment 4: Within the disease “Duchenne Muscular Dystrophy”, 
    # what are common eligibility criteria?
    logger.info("Analyzing common eligibility criteria for Duchenne Muscular Dystrophy.")
    analyze_eligibility_criteria(client, trials, indexing_records)

    # Assignment 5 and 6: 
    # Write a script which, for each patient, gets the clinical trials for 
    # that disease for our patient.
    # Write a script which, for each patient and for each clinical trial, 
    # scores the eligibility of the patient for that trial, using LLMs. 
    # This can be either on a scale of 0-10, or from categorical using 
    # eligible/ineligible/uncertain.
    logger.info("Determining eligibility for each trial per patient (capped at 10 trials).")
    determine_eligibility_per_trial(
        client,
        trials,
        indexing_records,
        patient_paths
    )


if __name__ == "__main__":
    main()
