import os
import sys
import json

from langchain_openai import ChatOpenAI
from browser_use.browser.browser import Browser, BrowserConfig
from browser_use import Agent, Browser, BrowserConfig,BrowserContextConfig,Controller,ActionResult
from browser_use.browser.context import BrowserContext
from dotenv import load_dotenv
import asyncio

load_dotenv()

browser = Browser(
        config=BrowserConfig(
        browser_binary_path='C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe',
        new_context_config=BrowserContextConfig(
			  keep_alive=True,
        ),
    ),
)

config = BrowserConfig(
    headless=False,
    disable_security=False
)
browser = Browser(config=config)

controller = Controller()

def is_google_forms(page) -> bool:
	return page.url.startswith('https://docs.google.com/forms/d/1DqRX94HQS_h16t0hJtwUj1Z1NqDWo5jnshMEBwXQ2IM/edit')

@controller.registry.action('Google forms: Open a blank form')
async def open_google_forms(browser: BrowserContext, google_form_url: str):
	page = await browser.get_current_page()
	if page.url != google_form_url:
		await page.goto(google_form_url)
		await page.wait_for_load_state()
	if not is_google_forms(page):
		return ActionResult(error='Failed to open Google form, are you sure you have permissions to access this form?')
	return ActionResult(extracted_content=f'Opened Google form {google_form_url}', include_in_memory=False)

QUESTION_TYPE_MAP = {
    'text': 'Short answer',
    'paragraph': 'Paragraph',
    'checkbox': 'Checkboxes',
    'dropdown': 'Dropdown',
    'date': 'Date',
    'time': 'Time',
}

async def set_question_type_if_needed(page, question_type):
    if question_type != 'multiple choice':
        label = QUESTION_TYPE_MAP.get(question_type)
        if label:
            await page.click('div[aria-label="question type"]')  
            await page.click(f'text="{label}"')       

async def add_question_to_form(page, question_data):
    # Add a question
    await page.click('text="Add Question"')  # Adjust selector as necessary

    # Insert question title
    if 'title' in question_data:
        await page.fill('textarea[name="question_title"]', question_data['title'])

    # Change question type
    await set_question_type_if_needed(page, q_type)

    q_type = question_data.get('type', 'text')

    # Choose question type
    if q_type == 'text':
        await page.click('text="Short answer"')

    elif q_type == 'paragraph':
        await page.click('text="Paragraph"')

    elif q_type == 'multiple_choice':
        await page.click('text="Multiple choice"')
        if 'choices' in question_data and question_data['choices']:
            for choice in question_data['choices']:
                await page.fill('input[placeholder="Option"]', choice)
                await page.press('input[placeholder="Option"]', 'Enter')

    elif q_type == 'checkbox':
        await page.click('text="Checkboxes"')
        if 'choices' in question_data and question_data['choices']:
            for choice in question_data['choices']:
                await page.fill('input[placeholder="Option"]', choice)
                await page.press('input[placeholder="Option"]', 'Enter')

    elif q_type == 'dropdown':
        await page.click('text="Dropdown"')
        if 'choices' in question_data and question_data['choices']:
            for choice in question_data['choices']:
                await page.fill('input[placeholder="Option"]', choice)
                await page.press('input[placeholder="Option"]', 'Enter')

    elif q_type == 'date':
        await page.click('text="Date"')

    elif q_type == 'time':
        await page.click('text="Time"')

    else:
        await page.click('text="Short answer"')  # Default fallback

    # Insert Add option
    if 'option' in question_data:
        await page.click('text="Add option"')

    # Common properties (help text, required)
    if 'helpText' in question_data and question_data['helpText']:
        await page.fill('textarea[name="description"]', question_data['helpText'])

    if 'required' in question_data and question_data['required']:
        #await page.click('input[aria-label="Required"]')  # Adjust this selector if needed
        required_checkbox = await page.query_selector('div[aria-label="필수"]')
        if required_checkbox:
            is_checked = await required_checkbox.get_attribute('aria-checked')
            if is_checked != 'true':
              await required_checkbox.click()

    return True

llm = ChatOpenAI(model="gpt-4o")

async def main():

    agent = Agent(
        task="Now create a complete Google Form following example. It should include a form title, exactly five questions, and add options based on question. for any question with choices, list the options—all specified with question text, question type, and whether it is required.  ",
        llm=llm,
		controller=controller,
    )

    result = await agent.run()
    print(result)

if __name__ == "__main__":
    asyncio.run(main())



'''

Prompting strategy :

1. Example for zero prompting


Now create a complete Google Form following example. 
It should include a form title, exactly five questions, and add options based on question. 
for any question with choices, list the options—all specified with question text, question type, and whether it is required.   
[
  {
    "title": "What is your full name?",
  },
  {
    "title": "What is your email address?",
  },
  {
    "title": "Which date(s) can you attend?",
  },
  {
    "title": "Do you have any dietary restrictions?",
  },
  {
    "title": "Any additional comments or questions?",
  }
]


2. Example for few-shot prompting

Form Title: Workshop Enrollment Form
1. What is your full name? (Short answer; "required : true")
2. please enter your Email address (Short answer; "required : true")
3. Which date(s) can you attend? (Checkbox:June 1st, June 2nd; "required: true")
4. Do you have any dietary restrictions? (Checkbox:"None", "Vegetarian", "Vegan", "Gluten-free", "Other"; "required")
5. Any additional comments or questions? (paragraph; "required : false")

Now create a complete Google Form following example. 
It should include a form title, exactly five questions, and add options based on question. 
for any question with choices, list the options—all specified with question text, question type, and whether it is required.       


[
  {
    "title": "What is your full name?",
  },
  {
    "title": "What is your email address?",
  },
  {
    "title": "Which date(s) can you attend?",
  },
  {
    "title": "Do you have any dietary restrictions?",
  },
  {
    "title": "Any additional comments or questions?",
  }
]

'''