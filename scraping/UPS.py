import os
import string
import time
import re

import slack_sdk
from dotenv import load_dotenv
from selenium import webdriver
from selenium.common import ElementClickInterceptedException, NoSuchElementException, WebDriverException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

import db

load_dotenv()

slack_token = os.getenv('TOKEN')
slack_channel_id = os.getenv('CHANNEL_ID')
client = slack_sdk.WebClient(token=slack_token)


def configure_ups_chromedriver():
    options = Options()
    options.add_argument('--headless')
    service = Service('/usr/local/bin/chromedriver')
    driver = webdriver.Chrome(service=service, options=options)
    driver.get('https://hcmportal.wd5.myworkdayjobs.com/en-US/Search/')
    return driver


class UPS:
    def __init__(self):
        self.ups_driver = configure_ups_chromedriver()
        time.sleep(7)

    def filter_ups_by_dev_location(self):
        try:
            self.ups_driver.find_element(By.CLASS_NAME, 'css-c8umoa').send_keys('software engineer')
            self.ups_driver.find_element(By.CLASS_NAME, 'css-12bdoy').click()
            self.ups_driver.find_element(By.CLASS_NAME, 'css-shvw01').click()
            time.sleep(7)
            location_btn = self.ups_driver.find_element(By.ID, 'location')  # click on location
            location_btn.click()
            time.sleep(5)
            self.ups_driver.find_element(By.ID, 'bc33aa3152ec42d4995f4791a106ed09').click()
            time.sleep(2)
            view_btn = self.ups_driver.find_element(By.XPATH, '//button[@data-automation-id="viewAllJobsButton"]')
            view_btn.click()
            time.sleep(2)
        except (ElementClickInterceptedException,
                NoSuchElementException,
                WebDriverException,
                ElementClickInterceptedException):
            print("Error in filter of UPS")

    def convert_title_to_db_objects(self, titles):
        title_list = []
        for title in range(len(titles)):
            text = [items.strip() for items in titles[title].split('\n') if items.strip()]
            title_list.append(text)
        return title_list

    def filter_by(self, titles) -> [string]:
        title_list = []
        for title in titles:
            # search for software engineer not senior or lead or intern
            if (title.text.lower().__contains__('lead') or
                    title.text.lower().__contains__('senior') or
                    title.text.lower().__contains__('specialist') or
                    title.text.lower().__contains__('intern') or
                    title.text.lower().__contains__('manager') or
                    title.text.lower().__contains__('sr') or
                    title.text.lower().__contains__('intermediate') or
                    title.text.lower().__contains__('chennai')):
                continue
            else:
                title_list.append(title.text)  # I need to add this to a database
        return title_list

    def make_ups_object(self, job_titles):
        for title in job_titles:
            print(title, end='\n')
            if len(title) >= 6:
                company_name = 'United Postal Services (UPS)'
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
                        elif '3 days ago' in title[-2].lower():
                            uploaded_days = 2
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
