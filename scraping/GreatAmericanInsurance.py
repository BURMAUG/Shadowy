import os
import re
import string

import slack_sdk
from selenium import webdriver
from selenium.common import ElementClickInterceptedException, NoSuchElementException, WebDriverException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from dotenv import load_dotenv
import time

import db

load_dotenv()

slack_token = os.getenv('TOKEN')
slack_channel_id = os.getenv('CHANNEL_ID')
client = slack_sdk.WebClient(token=slack_token)


class GreatAmericanInsurance:
    # given the webdriver to configure
    # given the url to open the page
    def __init__(self, chrome_path, url):
        self.position = None
        self.uploaded_days = None
        self.company_name = None
        self.chrome_options = Options()
        self.chrome_options.add_argument("--headless")
        self.service = Service(chrome_path)
        self.category = None
        self.path = chrome_path
        self.driver = webdriver.Chrome(service=self.service, options=self.chrome_options)
        self.driver.get(url)

    def click_job_category_btn(self, job_categories) -> None:
        for job_category in range(len(job_categories)):
            if job_category == 2:
                job_categories[job_category].click()
                break

    def select_tech_from_job_cat(self, categories) -> None:
        for self.category in range(len(categories)):
            if self.category == 3:
                categories[self.category].click()
                break
        time.sleep(3)
        try:
            view_jobs_btn = self.driver.find_element(By.CLASS_NAME, 'css-1t2z0wh')
            view_jobs_btn.click()
        except (ElementClickInterceptedException,
                NoSuchElementException,
                WebDriverException,
                ElementClickInterceptedException):
            print("Could not find select btn to click")

    def filter_by(self, titles) -> [string]:
        title_list = []
        for title in titles:
            # print(title.text)
            # search for software engineer not senior or lead or intern
            if (  # title.text.lower().__contains__('lead') or
                    # title.text.lower().__contains__('senior') or
                    title.text.lower().__contains__('intern') or
                    title.text.lower().__contains__('manager')):
                continue
            else:
                title_list.append(title.text)  # I need to add this to a database
        return title_list

    def convert_title_to_db_objects(self, titles):
        title_list = []
        for title in range(len(titles)):
            text = [items.strip() for items in titles[title].split('\n') if items.strip()]
            title_list.append(text)
        return title_list

    def make_gaic_object(self, job_titles):
        for title in job_titles:
            if len(title) == 6:
                company_name = 'Great American Insurance Company'
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
                                                    text=f"""{company_name.upper()} has a new opening for {position.upper()} and it was posted {uploaded_days} ago! APPLY NOW FOOL!""")
                    except (IndexError, ValueError) as e:
                        # Handle the exception (e.g., print an error message)
                        print(f"Error processing title: {title}. Error: {e}")
        db.connection.commit()
