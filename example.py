from handler.chatgpt_selenium_automation import ChatGPTAutomation

# Define the path where the chrome driver is installed on your computer
chrome_driver_path = "./chromedriver-linux64/chromedriver"

# the sintax r'"..."' is required because the space in "Program Files" in the chrome path
chrome_path = "/usr/bin/google-chrome"

# Create an instance
chatgpt = ChatGPTAutomation(chrome_path, chrome_driver_path)

# Define a prompt and send it to chatgpt
prompt = "What are the benefits of exercise?"
chatgpt.send_prompt_to_chatgpt(prompt)

# Retrieve previous conversations with ChatGPT
threads = chatgpt.get_chatgpt_threads(chatgpt)

# Retrieve the last response from ChatGPT
response = chatgpt.await_message_generation()

# Save the conversation to a text file
# file_name = "conversation.txt"
# chatgpt.save_conversation(file_name)

# Close the browser and terminate the WebDriver session
# chatgpt.quit()