import time
from handler.chatgpt_selenium_automation import ChatGPTAutomation
from templater import get_prompt

# Define the path where the chrome driver is installed on your computer
chrome_driver_path = "../chromedriver-linux64/chromedriver"

# the sintax r'"..."' is required because the space in "Program Files" in the chrome path
chrome_path = "/usr/bin/google-chrome"

# Create an instance
chatgpt = ChatGPTAutomation(chrome_path, chrome_driver_path)

# Define a prompt and send it to chatgpt
chat_name = "Game Builder"
concept_chat_name = "Concept Generator"
threads = chatgpt.get_chatgpt_threads()
thread_link = threads.get(concept_chat_name)
if thread_link:
    thread_link.click()
    time.sleep(2)

prompt = get_prompt(
    'concept_idea.txt',
    {
        'about': 'video game that has steampunk theme and goal is to find, craft items to '
                 'touch the sky. Come up with house designs that will be used for image generation.',
        'examples': '(like trains, motorbike etc.)'
    }
)
chatgpt.send_prompt_to_chatgpt(prompt)

# Retrieve previous conversations with ChatGPT

# Retrieve the last response from ChatGPT
response = chatgpt.await_message_generation()

# Save the conversation to a text file
# file_name = "conversation.txt"
# chatgpt.save_conversation(file_name)

# Close the browser and terminate the WebDriver session
# chatgpt.quit()