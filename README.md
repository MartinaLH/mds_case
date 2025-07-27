Getting started:

Activate the virtual environment:

 .\venv\Scripts\activate 

run the project:
python main.py

Things to improve:

- Make a Trial class that contains the data per trial

- Evaluate performance vs accuracy of calls to OpenAi
    - To determine the eligibility per trial, we now send each trial as a separate request. It would be nice to find out if sending each trial separately versus all of the trial at once makes a difference in speed and in the accuracy of the result.