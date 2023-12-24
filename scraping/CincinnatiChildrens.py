from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from dotenv import load_dotenv
from selenium.webdriver.support.wait import WebDriverWait

from Config.Configure import chrome_config

load_dotenv()

xpath = '//button[@class="au-target btn primary-button btn-lg phs-search-submit"]'


class CincinnatiChildrens:
    def __init__(self, url):
        self.driver = chrome_config(url)

    def filter_by_developers(self):
        try:
            search_box = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="typehead"]')))
            search_box.send_keys("developer")

            # Assuming xpath is defined somewhere before this point
            search_btn = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, xpath)))
            search_btn.click()

            # Wait for jobs to load, adjust the XPath if needed
            jobs = WebDriverWait(self.driver, 10).until(
                EC.presence_of_all_elements_located((By.XPATH, '//span[@data-ph-id="ph-page-element-page23-6NYZdX"]')))
            return jobs
        except Exception as e:
            print('Fault while filtering by developers', e)
