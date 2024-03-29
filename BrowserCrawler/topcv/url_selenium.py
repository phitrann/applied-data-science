import datetime
import json
import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By


SECOND_PAUSE_FOR_LOADING = 5    # setup 'n' second(s) for waiting the page to load
SECOND_PAUSE_FOR_SCROLLING = 1  # setup 'n' second(s) for waiting the page to scroll down to load full blocks job
NUMBER_PAGES_LOADING = 8        # setup the number of pages (there are 50 jobs/page load)
CURRENT_PAGE = 1                # the value for loop counter
PATH_URL = 'https://www.topcv.vn/viec-lam-it?page='
START_URL = PATH_URL + str(CURRENT_PAGE)
JOB_URLS = []                   # list to save the urls for each jobs get from blocks.

'''
    get_next_page_url()
    + Function to get the next page url
    + Return the next page url (str)
'''
def get_next_page_url():
    return PATH_URL + str(CURRENT_PAGE) 

# declare and setup variables for Chrome driver
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--disable-proxy-certificate-handler")
driver = webdriver.Chrome()
driver.get(START_URL)

# sleep code for loading page
time.sleep(SECOND_PAUSE_FOR_LOADING)

# Loop for get url jobs from each pageload.
while(CURRENT_PAGE <= NUMBER_PAGES_LOADING):
    print('payload: ', CURRENT_PAGE)
    # Scroll down to loading all blocks job.
    driver.execute_script("window.scrollTo(0, 1000)")
    time.sleep(SECOND_PAUSE_FOR_SCROLLING)

    # Get the block have list jobs.
    block_job_list = driver.find_elements(By.CLASS_NAME, 'block-job-list')
    job_cards = block_job_list[0].find_elements(By.CLASS_NAME, 'new-job-card')

    # get the url job in blocks job
    for block in job_cards:
        anchor_href = block.find_element(By.CSS_SELECTOR, 'a').get_attribute('href')
        JOB_URLS.append(anchor_href)

    # go to the next page
    CURRENT_PAGE += 1
    driver.get(get_next_page_url())


# Save the urls to file.json.
timenow = str(datetime.datetime.now().strftime("%Y-%m-%d"))
newpath = 'data/' + timenow + '.json'  
with open(newpath, 'w', encoding='utf-8') as of:
    json.dump(JOB_URLS, of, indent=4, default=str, ensure_ascii=False)

print('Done!')
# Close the browser Driver.
driver.close()
