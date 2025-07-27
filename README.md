**TLDR:**
This project analyzes some trial data and prints the results in the markdown file called `assignment_results.md` in the data folder.
You can check that markdown file for the results, or run the project yourself and recreate that file.


## Getting Started:

To get started, make sure you have Python 3.8 or higher installed.
You also need an OpenAI API key and the source data files.


### Installation

1. **Clone the repository** 

2. **Activate the virtual environment**:
    ```
   # Activate virtual environment (Windows)
   .\venv\Scripts\activate
   
   # Activate virtual environment (macOS/Linux)
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up OpenAI API key**:
   ```bash
   # Windows (Command Prompt)
   set OPENAI_API_KEY=your_api_key_here
   
   # Windows (PowerShell)
   $env:OPENAI_API_KEY="your_api_key_here"
   
   # macOS/Linux
   export OPENAI_API_KEY=your_api_key_here
   ```

5. **Make sure the needed source files are present in the data folder**:

    The project works with the following data files in the `data/` folder:
    - `payloads.jsonl` - Trial information data
    - `indexing_records.csv` - Trial indexing data
    - `patient_01.json`, `patient_02.json`, `patient_03.json` - Patient profiles


### Usage

To run the project:
```bash
python main.py
```

This will:
- Load and analyze trial data
- Count trials by phase
- Calculate average enrollments per phase
- Analyze top conditions
- Generate a report in `data/assignment_results.md`


### Things to improve:
- Improve code quality, by for example:
    - Making a Trial class that contains the data per trial
    - Reusing more code by splitting things up in reusable functions

- Add testing:
    - add unit tests
    - add actual checks for things that I manually checked (like if files exist etc.)

- Check if the OpenAI results actually make any sense, for example:
    - Check if the number of trials found seems accurate
    - Check if the eligibility criteria make sense

- Evaluate performance vs accuracy of calls to OpenAI
    - To determine the eligibility per trial, we now send each trial as a separate request. This is very slow, which is why the number of trials to check has been capped at 10.
    It would be nice to find out if sending each trial separately versus all of the trials at once makes a difference in speed and in the accuracy of the result.
