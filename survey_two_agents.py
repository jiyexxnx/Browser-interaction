import asyncio
from dotenv import load_dotenv
from browser_use import Browser, BrowserConfig, Agent
from langchain_openai import ChatOpenAI
import os

# load .env 
load_dotenv()

# Initialize Model
llm = ChatOpenAI(model="gpt-4o-mini")

# Browser config
browser = Browser(config=BrowserConfig(
    browser_binary_path=r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    user_data_dir=r"C:\\Users\\Bibbe\\AppData\\Local\\Google\\Chrome\\User Data",
    launch_args=[
        "--profile-directory=Default",
        "--no-first-run",
        "--no-default-browser-check",
    ]
))


# link to a precreated google form (empty)
form_url = "https://docs.google.com/forms/d/1zfJ1d5lEaYXHUIkbEZj9qjpuM-NZzs7kEbeCDY-bolE/edit"

# text-input -> base of the survey
text_for_survey = """
What is the GDPR? Europe’s new data privacy and security law includes hundreds of pages’ worth of new requirements for organizations around the world. This GDPR overview will help you understand the law and determine what parts of it apply to you.
The General Data Protection Regulation (GDPR) is the toughest privacy and security law in the world. Though it was drafted and passed by the European Union (EU), it imposes obligations onto organizations anywhere, so long as they target or collect data related to people in the EU. The regulation was put into effect on May 25, 2018. The GDPR will levy harsh fines against those who violate its privacy and security standards, with penalties reaching into the tens of millions of euros.
With the GDPR, Europe is signaling its firm stance on data privacy and security at a time when more people are entrusting their personal data with cloud services and breaches are a daily occurrence. The regulation itself is large, far-reaching, and fairly light on specifics, making GDPR compliance a daunting prospect, particularly for small and medium-sized enterprises (SMEs).
"""

async def main():
    # first agent creates survey based on text input, including some general questions about participant
    task_creator_agent = Agent(
    task=f"""
        You are given a task to create a five-question survey based on a given input text. The survey should ask for the participant's opinion about different aspects of the input. The first two questions must gather general information about the participant.

        Use a **variety of question types**: multiple-choice, short answer, dropdowns, and checkboxes. Be precise and clear in your wording.

        Follow the structure shown in the examples below. Do not google or open the browser. Return the survey in ENGLISH.

        ---

        ### EXAMPLE 1:

        Text:
        "This article discusses the increasing popularity of urban gardening in major cities. It highlights how community gardens promote sustainability, strengthen social bonds, and provide fresh produce to urban residents."

        Survey:
        1. **[Short answer]**  
        What is your age?

        2. **[Dropdown]**  
        What is your current place of residence?  
        - Urban area  
        - Suburban area  
        - Rural area  

        3. **[Multiple-choice]**  
        Have you ever participated in urban gardening?  
        - Yes  
        - No  
        - I’m not sure  

        4. **[Checkboxes]**  
        Which benefits of urban gardening do you find most relevant?  
        - Access to fresh food  
        - Community engagement  
        - Environmental impact  
        - Educational opportunities  

        5. **[Short answer]**  
        What other thoughts do you have about urban gardening?

        ---

        ### EXAMPLE 2:

        Text:
        "The article presents different perspectives on remote work and how it affects productivity, work-life balance, and communication among employees."

        Survey:
        1. **[Short answer]**  
        What is your current job title?

        2. **[Multiple-choice]**  
        Do you work remotely?  
        - Yes, full-time  
        - Yes, part-time  
        - No  

        3. **[Dropdown]**  
        How has remote work affected your productivity?  
        - Increased  
        - Decreased  
        - No significant change  

        4. **[Checkboxes]**  
        Which challenges have you faced while working remotely?  
        - Poor internet connection  
        - Lack of communication  
        - Distractions at home  
        - Feeling isolated  

        5. **[Short answer]**  
        What would improve your remote work experience?

        ---

        Now generate a survey for the following text:

        Text:
        {text_for_survey}
        """,
    browser=None,
    llm=llm,
)


    generated_task = await task_creator_agent.run()
    print("\nGenerated Task for Google Form:\n")
    print(generated_task)
    await asyncio.sleep(60)

     # second agent with added pause
    task = [
        f"""
        Your task is to open a specific Google Form (provided via URL) and add questions to it **without performing a Google search**.

        You will be given a list of survey questions and should follow these steps for each one:
        1. Click "Frage hinzufügen"
        2. Select the appropriate question type using the dropdown:
        - multiple-choice: select "Multiple Choice Question"
        - short answer: select "Kurzantwort"
        - dropdowns: select "Drop-down"
        - checkboxes: select "Kästchen"
        3. Insert the question text into the title field
        4. If available, insert the provided answer options

        At the end:
        - Remove the previous form title
        - Add a new, appropriate title based on the quiz content (no search allowed)

        ---

        ### EXAMPLE 1:

        **Form URL:** https://forms.gle/exampleform1

        **Generated Task:**
        1. [Short answer] What is your age?
        2. [Multiple-choice] What is your gender?  
        - Male  
        - Female  
        - Non-binary  
        - Prefer not to say  
        3. [Dropdown] How often do you use public transport?  
        - Daily  
        - A few times a week  
        - Rarely  
        - Never  
        4. [Checkboxes] Which services have you used in the past month?  
        - Bus  
        - Tram  
        - Subway  
        - Train  
        5. [Short answer] What could improve public transport in your area?

        **Expected Actions:**
        - Open form: https://forms.gle/exampleform1  
        - Add each question using the correct type and content  
        - Remove the old form title  
        - New title: "Public Transport Survey"

        ---

        ### EXAMPLE 2:

        **Form URL:** https://forms.gle/exampleform2

        **Generated Task:**
        1. [Short answer] What is your profession?
        2. [Multiple-choice] Do you enjoy working from home?  
        - Yes  
        - No  
        - Sometimes  
        3. [Dropdown] How many days a week do you work remotely?  
        - 0  
        - 1–2  
        - 3–4  
        - 5  
        4. [Checkboxes] What benefits do you associate with remote work?  
        - Flexibility  
        - No commuting  
        - More productivity  
        - Work-life balance  
        5. [Short answer] What challenges have you experienced while working from home?

        **Expected Actions:**
        - Open form: https://forms.gle/exampleform2  
        - Add each question correctly  
        - Replace the form title with: "Remote Work Feedback"

        ---

        Now do the same for the following input:

        **Form URL:** '{form_url}'

        **Generated Task:**  
        {generated_task}
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
