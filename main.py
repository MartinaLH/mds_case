#!/usr/bin/env python3
"""
Main entry point for the MDS case study.
Run this script from the mds_case directory.
"""

import logging
from project.trial_analyzer import (
    analyze_conditions,
    count_phases,
    initialize_assignment, 
    calculate_average_number_of_enrollments,
)


def main():
    """Main function to run the complete trial analysis workflow."""
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("main")
    
    logger.info("Starting MDS case study analysis...")
    
    # Initialize and load trial data
    trials = initialize_assignment()

    # Assignment 1: Count the number of trials in each phase
    logger.info("Counting the number of trials in each phase.")
    count_phases(trials)

    # Assignment 2: What is the average amount of (Estimated) Enrollments in a clinical trial in Phase 1, 2 and 3 each?
    logger.info("Calculating the average number of enrollments for each phase.")
    calculate_average_number_of_enrollments(trials)

    # Assignment 3: What are the top 10 most commonly studied conditions?
    logger.info("Calculating the top 10 most commonly studied conditions.")
    analyze_conditions(trials)





if __name__ == "__main__":
    main()
