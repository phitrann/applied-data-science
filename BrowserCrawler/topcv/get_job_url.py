import datetime
import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By

CURRENT_PAGE = 1
JOB_URLS = []
NUMBER_PAGES_LOADING = 5  # Number of pages
SECOND_PAGE_LOADING = 2    # Second for loading page
SECOND_SLEEP = 5          # Set seconds for avoiding connect to server continuously
START_URL = 'https://www.topcv.vn/viec-lam-it?page='

def get_next_page():
    return START_URL + str(CURRENT_PAGE)

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--disable-proxy-certificate-handler")
chrome_options.add_argument('log-level=3')
chrome_options.add_argument('headless')
driver = webdriver.Chrome(options = chrome_options)

while (CURRENT_PAGE <= NUMBER_PAGES_LOADING):
    ## Loading automate Chrome with first page.
    print('Page load:' + str(CURRENT_PAGE))
    driver.get(START_URL + str(CURRENT_PAGE))
    
    ## Waiting for loading page
    time.sleep(SECOND_PAGE_LOADING)

    job_block = driver.find_elements(By.CLASS_NAME, 'job-list-2')
    jobs_list = job_block[0].find_elements(By.CLASS_NAME, 'job-item-2')

    for block in jobs_list:
        # Find first tag name 'a' to get the job url.
        job_url = block.find_element(By.TAG_NAME, 'a').get_attribute('href')
        JOB_URLS.append(job_url)

    # Update
    CURRENT_PAGE += 1
    
    # Get time to sleep code to avoid connect to server continuously
    time.sleep(SECOND_SLEEP)

print('Saving job urls to json')
timenow = str(datetime.datetime.now().strftime("%Y-%m-%d"))
newpath = 'data/' + timenow + '.json'  
with open(newpath, 'w', encoding='utf-8') as of:
    json.dump(JOB_URLS, of, indent=4, default=str, ensure_ascii=False)
print('DONE !')
driver.close()