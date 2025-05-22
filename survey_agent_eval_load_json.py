import asyncio
from dotenv import load_dotenv
from browser_use import Browser, BrowserConfig, BrowserContextConfig, Agent
from langchain_openai import ChatOpenAI
import os
import json

# load .env 
load_dotenv()

# Initialize Model
llm = ChatOpenAI(model="gpt-4o-mini")

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

eval_questions = """
Titel = "Your Summer Vacation Plans 2025"
Question 1:
Question: Where are you planning to travel this summer?
Question Type: Short Answer
Required: Yes (required: true)
Question 2:
Question: How do you prefer to spend your summer vacation?
Question Type: Multiple Choice
Answer Options:
- Beach holiday
- City trip
- Active vacation (hiking, cycling, etc.)
- Relaxing at home
- Visiting family
- Something else
Required: Yes (required: true)
Question 3:
Question: Who are you spending your summer vacation with?
Question Type: Dropdown
Answer Options:
-Alone
-With partner
-With family
- With friends
- In a group trip
- Undecided
Required: Yes (required: true)
Question 4:
Question: What does vacation personally mean to you?
Question Type: Paragraph
Required: Yes (required: true)
Question 5:
Question: How excited are you about this year’s summer vacation?
Question Type: Linear Scale
Scale Range: 1 to 5
Label (Minimum): Not at all
Label (Maximum): Can’t wait
Required: Yes (required: true)
"""

# link to the google forms website
form_url = "https://docs.google.com/forms/u/0/?hl=de"


async def main():
    task = [
    """
    Please open the google forms website via this link: {form_url}
    Create a blank form and delete its current title, before adding the new title and these five questions, with correct question types and answering possibilities.
    Mark all questions as mandatory. 
    ---
    Title = "Your Summer Vacation Plans 2025"
    Question 1:
    Question: Where are you planning to travel this summer?
    Question Type: Short Answer
    Required: Yes (required: true)
    Question 2:
    Question: How do you prefer to spend your summer vacation?
    Question Type: Multiple Choice
    Answer Options:
    - Beach holiday
    - City trip
    - Active vacation (hiking, cycling, etc.)
    - Relaxing at home
    - Visiting family
    - Something else
    Required: Yes (required: true)
    Question 3:
    Question: Who are you spending your summer vacation with?
    Question Type: Dropdown
    Answer Options:
    - Alone
    - With partner
    - With family
    - With friends
    - In a group trip
    - Undecided
    Required: Yes (required: true)
    Question 4:
    Question: What does vacation personally mean to you?
    Question Type: Paragraph
    Required: Yes (required: true)
    Question 5:
    Question: How excited are you about this year’s summer vacation?
    Question Type: Linear Scale
    Scale Range: 1 to 5
    Label (Minimum): Not at all
    Label (Maximum): Can’t wait
    Required: Yes (required: true)
    ---
    - Use this URL to open the form website: {form_url}
    - Remember: Only five questions in random order. Title must be updated. Don't publish, just close when done.

    Here are two examples: 
    ## Example 1 (Demonstration of what to do):

    Input:
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

    Task:
    - Go to the Google Forms website and click "Blank Form"
    - Replace the title with "Favorite Beverages 2025"
    - Add the 5 questions in random order
    - Use correct question types
    - Add all answer options if provided
    - Enable the "Required" switch
    - Ensure only five questions total
    - Close the browser (do not publish)

    ## Example 2:

    Input:
    ---
    Title = "Daily Routine Habits"
    Question 1:
    Question: What time do you usually wake up?
    Question Type: Short Answer
    Required: Yes (required: true)
    Question 2:
    Question: Describe your typical morning routine.
    Question Type: Paragraph
    Required: Yes (required: true)
    Question 3:
    Question: How do you commute to work or school?
    Question Type: Multiple Choice
    Answer Options:
    - Car
    - Bike
    - Public Transport
    - Walk
    - I work/study from home
    Required: Yes (required: true)
    Question 4:
    Question: How many hours do you work or study per day?
    Question Type: Dropdown
    Answer Options:
    - Less than 4
    - 4 to 6
    - 6 to 8
    - More than 8
    Required: Yes (required: true)
    Question 5:
    Question: How satisfied are you with your daily routine?
    Question Type: Linear Scale
    Scale Range: 1 to 10
    Label (Minimum): Not at all
    Label (Maximum): Very satisfied
    Required: Yes (required: true)
    ---

    Task:
    - Open the Google Forms website and create a new form
    - Delete the standard title and change the form title to "Daily Routine Habits"
    - Add all five questions, in random order
    - Set the correct question type
    - Add answer options where applicable
    - Set all questions as required
    - Do not add any more than 5 questions
    - Close the browser afterward without submitting

    ## Your Turn:

    Input:
    ---
    Title = "Your Summer Vacation Plans 2025"
    Question 1:
    Question: Where are you planning to travel this summer?
    Question Type: Short Answer
    Required: Yes (required: true)
    Question 2:
    Question: How do you prefer to spend your summer vacation?
    Question Type: Multiple Choice
    Answer Options:
    - Beach holiday
    - City trip
    - Active vacation (hiking, cycling, etc.)
    - Relaxing at home
    - Visiting family
    - Something else
    Required: Yes (required: true)
    Question 3:
    Question: Who are you spending your summer vacation with?
    Question Type: Dropdown
    Answer Options:
    - Alone
    - With partner
    - With family
    - With friends
    - In a group trip
    - Undecided
    Required: Yes (required: true)
    Question 4:
    Question: What does vacation personally mean to you?
    Question Type: Paragraph
    Required: Yes (required: true)
    Question 5:
    Question: How excited are you about this year’s summer vacation?
    Question Type: Linear Scale
    Scale Range: 1 to 5
    Label (Minimum): Not at all
    Label (Maximum): Can’t wait
    Required: Yes (required: true)
    ---

    """
]


    form_filler_agent = Agent(
        task=task,  # overwritten in line 80
        browser=browser,
        llm=llm,
    )

    await form_filler_agent.run() 

# start function
if __name__ == "__main__":
    asyncio.run(main())


#.venv\Scripts\activate
