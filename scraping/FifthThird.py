import os
import re
import time

from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.common import ElementClickInterceptedException, NoSuchElementException, WebDriverException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from slack_sdk import WebClient


import db
from Config.Configure import strip_links_href

load_dotenv()

slack_token = os.getenv('TOKEN')
slack_channel_id = os.getenv('CHANNEL_ID')
client = WebClient(token=slack_token)


def configure_53_chromedriver():
    options = Options()
    options.add_argument('--headless')
    service = Service('/usr/local/bin/chromedriver')
    driver = webdriver.Chrome(service=service, options=options)
    driver.get("https://fifththird.wd5.myworkdayjobs.com/en-US/53careers/")
    return driver


class FifthThird:
    def __init__(self):
        self.driver = configure_53_chromedriver()
        time.sleep(5)

    def filter_by_dev(self):
        try:
            search_box = self.driver.find_element(By.CLASS_NAME, "css-c8umoa")
            search_box.send_keys("software engineer")
            time.sleep(10)
            search_btn = self.driver.find_element(By.CLASS_NAME, "css-nsxtx1")
            search_btn.click()
        except (ElementClickInterceptedException,
                NoSuchElementException,
                WebDriverException,
                ElementClickInterceptedException):
            print("Unable to locate Fifth Third filter btn")

    def convert_title_to_db_objects(self, titles):
        title_list = []
        for title in range(len(titles)):
            text = [items.strip() for items in titles[title].split('\n') if items.strip()]
            title_list.append(text)
        return title_list

    def filter_by(self, titles) -> [str]:
        title_list = []
        for title in titles:
            # search for software engineer not senior or lead or intern
            if (title.text.lower().__contains__('lead') or
                    title.text.lower().__contains__('senior') or
                    title.text.lower().__contains__('intern') or
                    title.text.lower().__contains__('manager')):
                continue
            else:
                title_list.append(title.text)  # I need to add this to a database
        return title_list

    def make_fifth_third_bank_object(self, job_titles):
        for title in job_titles:
            if len(title) == 6:
                company_name = 'FIFTH THIRD BANK (53 BANK)'
                position = title[0]
                if ('software' in position.lower() or
                        'developer' in position.lower() or
                        'application' in position.lower() or
                        'engineer' in position.lower()):
                    try:
                        if 'today' in title[-2].lower():
                            uploaded_days = 0
                        elif 'yesterday' in title[-2].lower():
                            uploaded_days = 1
                        else:
                            uploaded_days = int(re.findall(r'\d+', title[-2])[0])
                        db.cursor.execute(
                            '''SELECT company_name, position FROM job_db WHERE company_name = ? AND position = ?''',
                            (company_name, position))
                        row = db.cursor.fetchone()
                        print(company_name, position, uploaded_days)
                        if uploaded_days <= 2 and row is None:
                            db.cursor.execute(
                                'INSERT INTO job_db (company_name, position, posted) VALUES (?, ?, ?)',
                                (company_name, position, uploaded_days))
                            client.chat_postMessage(channel=slack_channel_id,
                                                    text=f"""{company_name.upper()} has a new opening for {position.upper()} and it was posted {uploaded_days} ago! APPLY NOW FOOL!!""")
                    except (IndexError, ValueError) as e:
                        # Handle the exception (e.g., print an error message)
                        print(f"Error processing title: {title}. Error: {e}")
        db.connection.commit()

