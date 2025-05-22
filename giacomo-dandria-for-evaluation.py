from browser_use import Agent, Browser, BrowserConfig
from browser_use import Controller
from browser_use.browser.context import BrowserContext, BrowserContextConfig
from langchain_openai import ChatOpenAI
import asyncio

import random
browser = Browser(
    config=BrowserConfig(
        #chrome_instance_path="C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
        headless=False,  # Run in non-headless mode for viewing
        disable_security=False,
        new_context_config=BrowserContextConfig(
			_force_keep_context_alive=True,
		),
    )
)


llm=ChatOpenAI(model='gpt-4o-mini', temperature=0.0)

controller = Controller()

async def main():

    setup_task = """Navigate to forms.google.com and create a new Google Form."""
    agent = Agent(task=setup_task, llm=llm, browser=browser, controller=controller, use_vision=False)
    await agent.run()

    set_title_and_description_task = f"""Look for the block that contains 'Untitled form', enter the title "The Present Simple Tense in English".
Click on the 'Form description' field and give the description "This form tests the knowledge of the present simple tense in English" ."""
    
    agent.add_new_task(set_title_and_description_task)
    await agent.run()

    # the following question types are accepted
    multiple_choice_task=f"""Click on field to input the question (it has the placeholder text 'Question' or 'Untitled question') and enter the question "Which of the following sentences is in the present simple tense?".
The first option must be inserted where the placeholder text is 'Option 1'. It is "He eats an apple every day.".
To add the second option, there is a field with placeholder text 'Add option'. Use the last 'Add option' field you find, not the first. Click on it and enter the second option "He is eating an apple.".
To add the third option, there is a field with placeholder text 'Add option'. Use the last 'Add option' field you find, not the first. Click on it and enter the third coption "He has eaten an apple."."""

    short_answer_task=f"""Click on field to input the question (it has the placeholder text like 'Question' or 'Untitled question') and enter the question "Write a sentence in the present simple tense.".
Click on the button to change the question-type accordingly to 'Short answer'."""

    paragraph_task=f"""Click on the 'Multiple choice' button and change the question-type to 'Paragraph'.
Click on field to input the question (it has the placeholder text 'Question' or 'Untitled question') and enter the prompt for the writing task "Write a short paragraph about your daily routine."."""

    checkboxes_task=f"""Click on the 'Multiple choice' button and change the question-type to 'Checkboxes'.
Make sure the question-type is 'Checkboxes' and not 'Multiple choice'.
If the type is still 'Multiple choice', click on the 'Multiple choice' button and change it to 'Checkboxes'.
Click on field to input the question (it has the placeholder text 'Question' or 'Untitled question') and enter the question "Which of the following sentences are in the present simple tense?".
The first option must be inserted where the placeholder text is 'Option 1'. It is "He eats an apple every day.".
To add the second option, there is a field with placeholder text 'Add option'. Use the last 'Add option' field you find, not the first. Click on it and enter the second option "He is eating an apple.".
To add the third option, there is a field with placeholder text 'Add option'. Use the last 'Add option' field you find, not the first. Click on it and enter the third option "Likes apples.".
To add the fourth option, there is a field with placeholder text 'Add option'. Use the last 'Add option' field you find, not the first. Click on it and enter the fourth option "He has eaten an apple."."""

    # we also need to add a task to add a new question, so we can add multiple questions
    add_new_question_task = f"""Click on the add question button to add another question. Do not add the question itself yet."""

    for i in range(5):

        # we randomly select one of the types between multiple choice, short answer, paragraph and checkboxes
        question_type = random.choice(['multiple_choice', 'short_answer', 'paragraph', 'checkboxes'])

        if question_type == 'multiple_choice':
            agent.add_new_task(multiple_choice_task)
            await agent.run()

        elif question_type == 'short_answer':
            agent.add_new_task(short_answer_task)
            await agent.run()

        elif question_type == 'paragraph':
            agent.add_new_task(paragraph_task)
            await agent.run()

        elif question_type == 'checkboxes':
            agent.add_new_task(checkboxes_task)
            await agent.run()

        # Add new blank question
        agent.add_new_task(add_new_question_task)
        await agent.run()

    input('Press Enter to close the browser...')
    await browser.close()

if __name__ == '__main__':
    asyncio.run(main())