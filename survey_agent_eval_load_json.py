import asyncio
import json
import os
from dotenv import load_dotenv
from browser_use import Browser, BrowserConfig, BrowserContextConfig, Agent
from langchain_openai import ChatOpenAI

# .env load
load_dotenv()

# url to the google forms page
form_url = "https://docs.google.com/forms/u/0/?hl=de"

# prompt example for few-shot
examples_text = """
## Example 1 (Demonstration of what to do):

Imagine you get this input:
---
Title = "Favorite Beverages 2025"
Question 1:
Question: What's your favorite drink?
Question Type: Short Answer
Required: Yes (required: true)
Question 2:
Question: When do you usually drink it?
Question Type: Paragraph
Required: Yes (required: true)
Question 3:
Question: Which of the following drinks do you enjoy?
Question Type: Multiple Choice
Answer Options:
- Coffee
- Tea
- Juice
- Water
- Soda
Required: Yes (required: true)
Question 4:
Question: With whom do you like to drink coffee or tea?
Question Type: Dropdown
Answer Options:
- Alone
- With friends
- With colleagues
- With family
Required: Yes (required: true)
Question 5:
Question: How important is your morning beverage?
Question Type: Linear Scale
Scale Range: 1 to 5
Label (Minimum): Not important
Label (Maximum): Absolutely essential
Required: Yes (required: true)
---

Then you go to the Google Forms website.
- Open the Google Forms website and create a new form
- Delete the standard Form Title "Unnamed Form" and set the form title to "Favorite Beverges 2025"
- Add a question and the title of the question
- Select the appropriate Question Type in the form
- Add all answer options where applicable
- Set the question as required
- Repeat the process for four more questions.
- Do not add any more than 5 questions
- Close the browser afterward without submitting
"""

# read json
def load_survey_json(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

# format json and add to the prompt --> got more stable results like this
def format_survey_for_prompt(survey_data):
    prompt = f"Title = \"{survey_data['title']}\"\n"
    for i, q in enumerate(survey_data["questions"], start=1):
        prompt += f"Question {i}:\n"
        prompt += f"Question: {q['question']}\n"
        prompt += f"Question Type: {q['type'].replace('_', ' ').title()}\n"
        if q.get("options"):
            prompt += "Answer Options:\n" + "\n".join(f"- {opt}" for opt in q["options"]) + "\n"
        if q.get("scale"):
            prompt += f"Scale Range: {q['scale']['min']} to {q['scale']['max']}\n"
            prompt += f"Label (Minimum): {q['scale']['label_min']}\n"
            prompt += f"Label (Maximum): {q['scale']['label_max']}\n"
        prompt += f"Required: Yes (required: {q['required']})\n"
    return prompt

# build final prompt function
def build_task_prompt(examples_text, survey_text, form_url):
    return f"""{examples_text}

## Your Turn:

Now do the same for the following input:
---
{survey_text}---
- Use this URL to open the form website: {form_url}
- Remember: Only five questions in random order. Title must be updated. Don't publish, just close when done.
- Remember to select the according question type: Short Answer, Long Answer, Linear Scale, Multiple Choice & Dropdown
"""

# main async-Funktion
async def main():

    # load .env 
    load_dotenv()

    # Initialize Model
    llm = ChatOpenAI(model="o4-mini")

    # Browser config
    browser = Browser(
        config=BrowserConfig(
        browser_binary_path='C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
        new_context_config=BrowserContextConfig(
        keep_alive=True,
    ),
    ))

    config=BrowserConfig(
        headless=False,
        disable_security=False,
    )

    browser = Browser(config=config)
    
    # read json and build prompt
    survey_data = load_survey_json("eval_dataset.json")
    survey_text = format_survey_for_prompt(survey_data)
    full_task = build_task_prompt(examples_text, survey_text, form_url)

    # use 4o mini
    llm = ChatOpenAI(model="gpt-4o-mini")

    # agent initializiation & run
    agent = Agent(
        task=[full_task],
        browser=browser,
        llm=llm,
    )

    await agent.run()

# main-function
if __name__ == "__main__":
    asyncio.run(main())
