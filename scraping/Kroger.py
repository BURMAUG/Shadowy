import os
import re
from datetime import datetime

from dotenv import load_dotenv
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

import db
from Config.Configure import chrome_config, client
from selenium.webdriver.support import expected_conditions as EC

load_dotenv()
slack_token = os.getenv("TOKEN")
slack_channel = os.getenv("CHANNEL_ID")
url = os.getenv("KROGER_URL")
search_path = 'class="search-box-compact__input text-color-primary ui-autocomplete-input"'
search_btn_path = 'search-box-compact__button'


class Kroger(object):
    def __init__(self, url):
        self.driver = chrome_config(url)

    def filter_by_software(self) -> None:
        search_box = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH,
                                                                                          f"//*[@{search_path}]")))
        search_box.send_keys("software engineer")
        # time.sleep(10)
        search_btn = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME,
                                                                                          'search-box-compact__button')))
        self.driver.execute_script("arguments[0].click();", search_btn)

    def get_software_lis(self) -> [str]:
        search_li = WebDriverWait(self.driver, 10).until(EC.presence_of_all_elements_located((By.XPATH,
                                                                                              '//*[@data-qa'
                                                                                              '="searchResultItem"]')))
        job_list = [element.text for element in search_li]
        return job_list

    def to_object(self, job_list: [str]) -> None:
        company_name = 'KROGER TECHNOLOGIES (KRG)'

        for job in job_list:
            lines = job.split('\n')
            position = lines[0]
            try:
                if len(lines) > 1:
                    uploaded_date = lines[1]
                    uploaded_days = re.findall(r'\b\d{2}/\d{2}/\d{4}\b', uploaded_date)
                    if uploaded_days:
                        uploaded_day = datetime.now() - datetime.strptime(uploaded_days[0], '%m/%d/%Y')

                        db.cursor.execute(
                            '''SELECT company_name, position FROM job_db WHERE company_name = ? AND position = ?''',
                            (company_name, position))

                        row = db.cursor.fetchone()

                        if uploaded_day.days <= 2 and row is None:
                            db.cursor.execute(
                                '''INSERT INTO job_db (company_name, position, posted) VALUES (?, ?, ?)''',
                                (company_name, position, uploaded_day.days))

                            client.chat_postMessage(
                                channel=slack_channel,
                                text=f"{company_name.upper()} has a new opening for {position.upper()} and it was posted {uploaded_day.days} days ago! APPLY NOW!"
                            )
                    print(company_name, position, uploaded_days)
            except Exception as e:
                print(e)

        db.connection.commit()
        db.connection.close()