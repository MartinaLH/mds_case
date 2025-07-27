import logging
from pandas import DataFrame
import os
import openai
from typing import List
import json

from pydantic import BaseModel

from project.file_reader import append_to_markdown_file

INDEXING_RECORDS_PATH = "data/indexing_records.csv"
TRIAL_INFORMATION_PATH = "data/payloads.jsonl"
PATIENT_01_PATH = "data/patient_01.json"
PATIENT_02_PATH = "data/patient_02.json"
PATIENT_03_PATH = "data/patient_03.json"

logger = logging.getLogger(__name__.split('.')[-1])

# Suppress HTTPX logs from OpenAI client to avoid cluttering the output
openai._utils._logs.httpx_logger.setLevel(logging.WARNING)


class EligibilityScore(BaseModel):
    description: str
    score: float


def initiate_openai_client() -> openai.OpenAI:
    key = os.getenv('OPENAI_API_KEY')

    if not key:
        raise ValueError("OPENAI_API_KEY environment variable is not set.")

    client = openai.OpenAI(api_key=key)
    return client


def analyze_eligibility_criteria(
    client: openai.OpenAI, 
    trial_data: List[dict], 
    indexing_records: DataFrame
) -> None:

    # Get unique conditions to analyze
    unique_conditions = indexing_records['a.alias'].unique().tolist()

    # Find descriptions matching Duchenne Muscular Dystrophy
    relevant_conditions = find_duchenne_muscular_dystrophy_conditions(
        client, unique_conditions
    )

    # Find trials related to these conditions
    relevant_trials = find_trials_per_condition(
        relevant_conditions, indexing_records
    )

    relevant_trial_data = [
        trial for trial in trial_data
        if trial.get('utn') in relevant_trials
    ]

    elegibility_criterias = [
        trial.get('eligibility') for trial in relevant_trial_data
        if trial.get('eligibility') is not None
    ]

    # Find  and analyse common elegibility criteria for these trials
    eligibility_criteria = find_common_eligibility_criteria(
        client, 
        elegibility_criterias
    )

    logger.info("Found common eligibility criteria for Duchenne Muscular Dystrophy trials.")
    print_eligibility_criteria(eligibility_criteria)


def print_eligibility_criteria(eligibility_criteria: str) -> None:
    """
    Print the eligibility criteria in a formatted way.
 
    Args:
        eligibility_criteria (str): The eligibility criteria to print.
    """
      
    markdown_content = "## Assignment 4\n\n"
    markdown_content += "### Common Eligibility Criteria for Duchenne Muscular Dystrophy Trials\n\n"
    markdown_content += "The common eligibility criteria for Duchenne Muscular Dystrophy trials are:\n\n"
    markdown_content += f"{eligibility_criteria}\n\n"

    # Write to markdown file
    append_to_markdown_file(markdown_content)


def find_condition_list_in_response(response_text: str) -> List[str]:
    """
    Extracts a JSON array from the response text.

    Args:
        response_text (str): The text response from OpenAI containing a JSON array.

    Returns:
        List[str]: A list of strings parsed from the JSON array.
    """
    start_idx = response_text.find('[')
    end_idx = response_text.rfind(']') + 1
    if start_idx != -1 and end_idx > start_idx:
        json_str = response_text[start_idx:end_idx]
        return json.loads(json_str)
    return []


def find_duchenne_muscular_dystrophy_conditions(
    client: openai.OpenAI, 
    unique_conditions: List[str]
) -> List[str]:

    # Split the conditions found in the indexing records into manageable batches
    batch_size = 100
    all_related_conditions = []

    for i in range(0, len(unique_conditions), batch_size):
        conditions_subset = unique_conditions[i:i+batch_size]

        example_list = [
            "Duchenne Muscular Dystrophy",
            "Muscular Dystrophy, Duchenne",
            "DMD",
            "Duchenne's disease"
        ]

        prompt = f"""
        You are a medical expert analyzing clinical trial conditions. 
        I need you to analyze a list of diseases and identify the ones that 
        are Duchenne Muscular Dystrophy, considering various naming conventions.
        Please analyze this list of medical conditions and return ONLY a JSON 
        array containing the conditions:

        {conditions_subset}

        Return your response as a valid JSON array of strings, like this:
        ["condition1", "condition2", "condition3"]

        Only include conditions that are  Duchenne Muscular Dystrophy itself 
        (various naming conventions). 
        For example, "{', '.join(example_list)}", etc.

        If no conditions in this list are related to Duchenne Muscular
        Dystrophy, return an empty array: []
        """
        content = """
        You are a medical expert specializing in muscular dystrophies and
        neuromuscular disorders.
        """
        # Make the API call
        response = client.chat.completions.create(
            model="gpt-4o-2024-08-06",
            messages=[
                {"role": "system", "content": content},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1
        )

        # Parse the response and convert it to a list of conditions
        response_text = response.choices[0].message.content.strip()
        conditions = find_condition_list_in_response(response_text)
      
        if len(conditions) == 0:
            logger.debug("No matching conditions found in this batch.")
            continue

        all_related_conditions.extend(conditions)

    # Fail-safe in case no conditions are found at all 
    if len(all_related_conditions) == 0:
        print("No conditions related to Duchenne Muscular Dystrophy found.")
        all_related_conditions = example_list

    logger.info(f"Found {len(all_related_conditions)} conditions.")
    return all_related_conditions


def find_common_eligibility_criteria(
    client: openai.OpenAI,
    eligibility_criterias: List[dict]
) -> str:
    content = """
    You are a clinical research expert analyzing clinical trial data. 
    Focus on providing specific, actionable information about eligibility 
    criteria.
    """

    response = client.chat.completions.create(
        model="gpt-4o-2024-08-06",
        messages=[
            {
                "role": "system", 
                "content": content
            },
            {
                "role": "user", 
                "content": f"""Within the disease "Duchenne muscular dystrophy", 
                what are common eligibility criteria? 

                Please analyze clinical trials data and provide:
                1. Common inclusion criteria
                2. Common exclusion criteria  
                3. Age ranges typically studied
                4. Any biomarker or diagnostic requirements
                5. Treatment history requirements

                These are the eligibility criteria found in the trials:
                {eligibility_criterias}"""
            }
        ],
        max_tokens=1000,
        temperature=0.1
    )

    logger.info("Common eligibility criteria found for Duchenne Muscular Dystrophy trials.")
    return response.choices[0].message.content


def find_trials_per_condition(
        conditions: List[str], 
        indexing_records: DataFrame
) -> List[str]:
    relevant_trials = (
        indexing_records[indexing_records['a.alias'].isin(conditions)]['s.id']
        .unique()
        .tolist()
    )
    logger.info(
        f"Found {len(relevant_trials)} trials related to conditions '{', '.join(conditions)}'."
    )
    return relevant_trials


def load_patient_data(patient_path: str) -> dict:
    if os.path.exists(patient_path):
        with open(patient_path, 'r', encoding='utf-8') as file:
            return json.loads(file.read())
    else:
        logger.error(f"Patient data file {patient_path} does not exist.")
        return {}


def find_trials_per_patient(
    patient_data: dict,
    indexing_records: DataFrame
) -> List[str]:
    condition = patient_data['profile']['condition']
    logger.debug(f"Searching for trials related to patient condition: {condition}")

    relevant_trials = find_trials_per_condition([condition], indexing_records)
    return relevant_trials


def determine_eligibility_score(
    client: openai.OpenAI,
    patient_profile: str,
    eligibility_criteria: dict
) -> float:  
    prompt = f"""
    You are a clinical trial expert. Determine the eligibility score based on:
     - Information about the patient found in the patient profiles.
     - The eligibility criteria for the trial.

    The information about the patient profiles can be found in 
    the patient profile {patient_profile}:

    The eligibility criteria for the trial are: {eligibility_criteria}
    Please provide a score from 0 to 10 based on how well the patient 
    profile matches the eligibility criteria.
   
    Please provide the response as a float number between 0 and 10, where:
    - 0 means the patient does not meet any of the criteria
    - 10 means the patient meets all of the criteria

    Don't include any additional text or reasoning, just return the score
    as a float number.

    """

    response = client.chat.completions.parse(
        model="gpt-4o-2024-08-06",
        messages=[
            {"role": "system", "content": "You are a clinical trial expert."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.1,
        response_format=EligibilityScore
    )

    eligibility_score = response.choices[0].message.parsed

    return eligibility_score.score


def determine_eligibility_per_trial(
    client: openai.OpenAI,
    trial_data: List[dict],
    indexing_records: DataFrame,
    patient_paths: List[str]
) -> None:
    trial_scores_per_patient: List[List[dict]] = []

    for patient_path in patient_paths:
        patient_data = load_patient_data(patient_path)

        relevant_trials = find_trials_per_patient(
            patient_data,
            indexing_records
        )

        patient_profile = patient_data['profile']['profile']

        trial_scores = {}

        # Since some of the conditions have hunderds of trials,
        # making it take a long time to process all of them,
        # we limit the number of trials to 10 to keep it quickly runnable
        relevant_trials = relevant_trials[:10]

        for trial_id in relevant_trials:
            trial_information = next(
                (trial for trial in trial_data if trial.get('utn') == trial_id),
                None
            )

            eligibility_criteria = trial_information['eligibility']

            eligibility_score = determine_eligibility_score(
                client, patient_profile, eligibility_criteria
            )
            trial_scores[trial_id] = eligibility_score
            logger.debug(
                f"Eligibility score for trial {trial_id}: {eligibility_score}"
            )

        trial_scores_per_patient.append(trial_scores)  
    print_trial_scores(trial_scores_per_patient)


def print_trial_scores(trial_scores_per_patient: List[List[dict]]) -> None:
    """
    Print the trial scores for each patient in a formatted way.

    Args:
        trial_scores_per_patient (List[List[dict]]): The trial scores for each patient.
    """
    markdown_content = "## Assignment 5 and 6\n\n"
    markdown_content += "### Eligibility Scores for Patients in Clinical Trials\n\n"

    for i, trial_scores in enumerate(trial_scores_per_patient):
        markdown_content += f"### Patient {i + 1} Trial Scores:\n\n"
        for trial_id, score in trial_scores.items():
            markdown_content += f"- Trial ID: {trial_id}, Eligibility Score: {score}\n"
        markdown_content += "\n"

    append_to_markdown_file(markdown_content)
