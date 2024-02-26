import os
from multiprocessing import Process

from dotenv import load_dotenv
from selenium.common import ElementClickInterceptedException
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.support.wait import WebDriverWait

# import Config
# from Config.Configure import strip_links_href
# from scraping.CincinnatiChildrens import CincinnatiChildrens
from scraping.FifthThird import FifthThird
from scraping.GreatAmericanInsurance import GreatAmericanInsurance
from selenium.webdriver.common.by import By
import time

from scraping.Kroger import Kroger
from scraping.UPS import UPS
from scraping.USBank import USBank

load_dotenv()
# ------------------------------- VARIABLES -----------------------------------
chromedriver_path = '/usr/local/bin/chromedriver'


def scrape_GAIC():
    global titles
    try:
        gaic = GreatAmericanInsurance(chromedriver_path, os.getenv('GAIC_URL'))
        time.sleep(2)

        # select categories
        job_categories = gaic.driver.find_elements(By.CLASS_NAME, 'css-1lw9q8d')
        gaic.click_job_category_btn(job_categories)
        time.sleep(3)

        # select technology and view jobs
        select_tech = gaic.driver.find_elements(By.CLASS_NAME, 'css-fuxn0n')
        gaic.select_tech_from_job_cat(select_tech)
        time.sleep(5)

        # search by sending the keyword developer
        search_bar = gaic.driver.find_element(By.CLASS_NAME, 'css-10mv5a0')  # this should be the search bar
        search_btn = gaic.driver.find_element(By.CLASS_NAME, 'css-95sf2f')
        search_bar.send_keys('developer')
        search_btn.click()
        time.sleep(4)
        # this should be the links gotten
        link_list = gaic.driver.find_elements(By.CLASS_NAME, 'css-19uc56f')
        for link in link_list:
            if 'developer' in link.get_attribute('href'):
                print(f'Link: {link.get_attribute("href")}')
        # filter by seniority then send me and email about the job and then add it into the database
        titles = gaic.driver.find_elements(By.CLASS_NAME, 'css-1q2dra3')

        job_description = gaic.filter_by(titles)
        # print( "GAIC ", job_description)
        list = gaic.convert_title_to_db_objects(job_description)
        gaic.make_gaic_object(list)

        time.sleep(2)
        gaic.driver.quit()
    except FileNotFoundError:
        print("Something terrible happened with GAIC")


def scrape_UPS():
    try:
        ups = UPS()
        ups.filter_ups_by_dev_location()
        list_devs = ups.ups_driver.find_elements(By.CLASS_NAME, 'css-1q2dra3')
        list_tit = ups.filter_by(list_devs)
        op = ups.convert_title_to_db_objects(list_tit)
        ups.make_ups_object(op)
        time.sleep(3)
        ups.ups_driver.quit()
    except ElementClickInterceptedException:
        print("Something terribly happened with UPS")


def scrape_USB():
    global objects
    try:
        us_bank = USBank()
        time.sleep(4)
        us_bank.filter_by_dev_location()
        list_div = us_bank.driver.find_elements(By.CLASS_NAME, 'css-1q2dra3')
        list_title = us_bank.filter_by(list_div)
        objects = us_bank.convert_title_to_db_objects(list_title)
        us_bank.make_usbank_object(objects)
        us_bank.driver.quit()
    except FileNotFoundError:
        print("Something terribly happened with US BANK")


def scrape_53():
    global titles, objects
    try:
        fifth_third = FifthThird()
        fifth_third.filter_by_dev()
        time.sleep(10)
        list_dev = fifth_third.driver.find_elements(By.XPATH, '//li[contains(@class, "css-1q2dra3")]')
        titles = fifth_third.filter_by(list_dev)
        # look_href = WebDriverWait(fifth_third.driver, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME,
        #                                                                                       "css-19uc56f")))
        # strip_links_href(look_href)
        objects = fifth_third.convert_title_to_db_objects(titles)
        fifth_third.make_fifth_third_bank_object(objects)
        fifth_third.driver.quit()
    except FileNotFoundError:
        print("Something terrible happened with 53 BANK")


# def scrape_CCH():
#     global c, titles
#     try:
#         c = CincinnatiChildrens(os.getenv('CHILDRENS'))
#         jobs = c.filter_by_developers()
#         titles = Config.Configure.convert_to_str_cch(jobs=jobs)
#         Config.Configure.make_cch_object(job_titles=titles)
#         c.driver.quit()
#     except FileNotFoundError:
#         print('Something terribly happened with Cincinnati children\'s')


def scrape_KRG():
    global lists
    try:
        krg = Kroger(os.getenv('KROGER_URL'))
        krg.filter_by_software()
        lists = krg.get_software_lis()
        krg.to_object(lists)
        krg.driver.quit()
    except FileNotFoundError:
        print("Something terribly happened with Kroger")


if __name__ == '__main__':
    # while True:
    processes = [
        Process(target=scrape_GAIC),
        Process(target=scrape_UPS),
        Process(target=scrape_USB),
        Process(target=scrape_53),
        Process(target=scrape_KRG)
    ]
    for process in processes:
        process.start()
    for process in processes:
        process.join()
