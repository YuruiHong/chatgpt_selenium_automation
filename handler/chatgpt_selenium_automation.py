import asyncio
import time
import socket
import threading
import os
from collections import deque

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import requests
from urllib.parse import urlparse, unquote

IMAGE_PATH = '/home/bayram/byk/chatgpt_selenium_automation/image'


class ChatGPTAutomation:

    def __init__(self, chrome_path, chrome_driver_path, profile_directory=None, skip_human_verification=False, prefix="", suffix=""):
        """
        This constructor automates the following steps:
        1. Open a Chrome browser with remote debugging enabled at a specified URL.
        2. Prompt the user to complete the log-in/registration/human verification, if required.
        3. Connect a Selenium WebDriver to the browser instance after human verification is completed.

        :param chrome_path: file path to chrome.exe (ex. C:\\Users\\User\\...\\chromedriver.exe)
        :param chrome_driver_path: file path to chrome.exe (ex. C:\\Users\\User\\...\\chromedriver.exe)
        """

        self.chrome_path = chrome_path
        self.chrome_driver_path = chrome_driver_path
        self.prefix = prefix
        self.suffix = suffix

        url = r"https://chat.openai.com"
        free_port = self.find_available_port()
        self.launch_chrome_with_remote_debugging(free_port, url, profile_directory)
        self.driver = self.setup_webdriver(free_port)
        if not skip_human_verification:
            self.wait_for_human_verification()

    def find_available_port(self):
        """ This function finds and returns an available port number on the local machine by creating a temporary
            socket, binding it to an ephemeral port, and then closing the socket. """

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('', 0))
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            return s.getsockname()[1]

    def launch_chrome_with_remote_debugging(self, port, url, profile_directory=None):
        """ Launches a new Chrome instance with remote debugging enabled on the specified port and navigates to the
            provided url """

        def open_chrome():
            chrome_cmd = f"{self.chrome_path} --remote-debugging-port={port}"
            if profile_directory:
                chrome_cmd += f" --profile-directory='{profile_directory}'"
            chrome_cmd += f" {url}"
            os.system(chrome_cmd)

        chrome_thread = threading.Thread(target=open_chrome)
        chrome_thread.start()

    def setup_webdriver(self, port):
        """  Initializes a Selenium WebDriver instance, connected to an existing Chrome browser
             with remote debugging enabled on the specified port"""

        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_experimental_option("debuggerAddress", f"127.0.0.1:{port}")
        driver = webdriver.Chrome(executable_path=self.chrome_driver_path, options=chrome_options)
        return driver

    @staticmethod
    def are_elements_same(queue):
        if not queue:
            return True

        if len(queue) < queue.maxlen:
            return False

        first_element = queue[0]
        for element in queue:
            if element != first_element:
                return False

        return True

    async def check_message_generation(self):
        values = deque(maxlen=5)
        last_response = self.return_last_response()
        values.append(hash(last_response))

        await asyncio.sleep(0.3)
        while not self.are_elements_same(values):
            await asyncio.sleep(0.5)
            last_response = self.return_last_response()
            values.append(hash(last_response))

        return last_response

    def await_message_generation(self):
        return asyncio.run(self.check_message_generation())

    def send_prompt_to_chatgpt(self, prompt):
        input_box = self.driver.find_element(
            by=By.XPATH, value='//textarea[contains(@placeholder, "Message ChatGPT…")]'
        )
        prompt = prompt.replace("\\\'", "'").replace("'", "\\'").replace("\n", "\\n")
        self.driver.execute_script(f"arguments[0].value = '{self.prefix}\\n{prompt}\\n{self.suffix}';", input_box)
        input_box.send_keys(Keys.RETURN)
        input_box.submit()
        time.sleep(.9)

    def return_chatgpt_conversation(self):
        """
        :return: returns a list of items, even items are the submitted questions (prompts) and odd items are chatgpt response
        """

        return self.driver.find_elements(by=By.CSS_SELECTOR, value='div.text-base')

    def get_chatgpt_threads(self):
        uuid_pattern = "/c/"
        elements = self.driver.find_elements(
            by=By.XPATH, value=f'//a[contains(@href, "{uuid_pattern}")]'
        )
        return {element.text: element for element in elements}

    def check_login(self):
        button_text = "Log in"

        elements = self.driver.find_elements(By.XPATH, f'//*[contains(text(), "{button_text}")]')
        return len(elements) > 2

    def find_images(self):
        images = []
        elements = self.driver.find_elements(By.XPATH, '//*[@src]')
        for element in elements:
            src = element.get_attribute('src')
            if src and src.startswith('https://files'):
                images.append(src)
        return images

    @staticmethod
    def download_image(image_url, file_name):
        response = requests.get(image_url)
        if response.status_code == 200:
            with open(file_name, 'wb') as file:
                file.write(response.content)

    @staticmethod
    def list_files(directory):
        try:
            # List all files and directories in the given directory
            files = os.listdir(directory)
            return files
        except FileNotFoundError:
            return "Directory not found."

    def save_conversation(self, file_name, otype='w', last_index=None):
        """
        It saves the full chatgpt conversation of the tab open in chrome into a text file, with the following format:
            prompt: ...
            response: ...
            delimiter
            prompt: ...
            response: ...

        :param file_name: name of the file where you want to save
        """
        directory_name = "conversations"
        if not os.path.exists(directory_name):
            os.makedirs(directory_name)
        file_path = os.path.join(directory_name, file_name)
        # raw_limilation_errors = ["ChatGPT\nYou've reached our limit of messages per hour. Please try again later.", "ChatGPT\nToo many requests in 1 hour. Try again later."]
        raw_limilation_errors = ["ChatGPT"]
        

        chatgpt_conversation = self.return_chatgpt_conversation()
        conversation_length = len(chatgpt_conversation)
        if last_index:
            with open(file_path, otype) as file:
                for i in range(0, conversation_length, 4):
                    last_index += 1
                    answer = chatgpt_conversation[i+2].text.split('\n')[1]
                    if answer in raw_limilation_errors:
                        break
                    file.write("\n"+str(last_index)+" "+answer)
        else:
            with open(file_path, otype) as file:
                for i in range(0, conversation_length, 4):
                    answer = chatgpt_conversation[i+2].text.split('\n')[1]
                    if answer in raw_limilation_errors:
                        break
                    file.write("\n"+answer)

    def return_last_response(self):
        """ :return: the text of the last chatgpt response """

        response_elements = self.driver.find_elements(by=By.CSS_SELECTOR, value='div.text-base')
        return response_elements[-1].text

    def wait_for_human_verification(self):
        print("You need to manually complete the log-in or the human verification if required.")

        while True:
            if self.check_login():
                break

            user_input = input(
                "Enter 'y' if you have completed the log-in or the human verification, or 'n' to check again: ").lower()

            if user_input == 'y':
                print("Continuing with the automation process...")
                break
            elif user_input == 'n':
                print("Waiting for you to complete the human verification...")
                time.sleep(5)  # You can adjust the waiting time as needed
            else:
                print("Invalid input. Please enter 'y' or 'n'.")

    def quit(self):
        """ Closes the browser and terminates the WebDriver session."""
        print("Closing the browser...")
        self.driver.close()
        self.driver.quit()
