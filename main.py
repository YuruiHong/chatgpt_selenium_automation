from handler.chatgpt_selenium_automation import ChatGPTAutomation
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from time import sleep
import os

os.environ['DISPLAY'] = ':0' 

# Define the path where the chrome driver is installed on your computer
chrome_driver_path = r"/home/hyr/.wdm/drivers/chromedriver/linux64/120.0.6099.109/chromedriver-linux64/chromedriver"

# the sintax r'"..."' is required because the space in "Program Files" in the chrome path
chrome_path = r'/usr/bin/chromium'

# Create an instance
prefix = "Answer this multiple choice question. Your full response should only contain the digit index of the answer in choices. Do not explain. Ignore lack of information. Guess if necessary. Just give one digit."

os.system("killall chromiumdriver")

for profile in ["Default", "Profile 1", "Profile 2", "Profile 3", "Profile 4", "Profile 5", "Profile 7"]:
    try:
        os.system("killall chromium")
        chatgpt = ChatGPTAutomation(chrome_path, chrome_driver_path, profile_directory=profile, skip_human_verification=True, prefix=prefix)

        wait = WebDriverWait(chatgpt.driver, 10)
        wait.until(EC.presence_of_element_located((By.ID, 'prompt-textarea')))
        sleep(3)
        file_name = "conversation.txt"
        directory_name = "conversations"
        if not os.path.exists(directory_name):
            os.makedirs(directory_name)
        file_path = os.path.join(directory_name, file_name)
        last_index = None
        with open(file_path, 'r') as file:
            file.seek(0, os.SEEK_END)
            file.seek(file.tell() - 1, os.SEEK_SET)
            while file.read(1) != '\n':
                file.seek(file.tell() - 2, os.SEEK_SET)
            last_line = file.readline()
            last_index = int(last_line.split(' ')[0])
    except:
        last_index = -1
    problems_path = "test.txt"
    try:
        with open(problems_path, "r") as f:
            problems = f.readlines()
            chatgpt.send_prompt_to_chatgpt(problems[last_index+1])
            sleep(5)
            for i in range(last_index+2, len(problems)):
                chatgpt.send_prompt_to_chatgpt(problems[i])
                sleep(3)
    except Exception as e:
        print(e)
    try:
        chatgpt.save_conversation(file_name, otype='a', last_index=last_index)
    except Exception as e:
        pass
    try:
        chatgpt.quit()
    except Exception as e:
        pass
