import pandas as pd
import time
import urllib
from math import ceil
import random
import os

# import selenium
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.action_chains import ActionChains

# ignore warning
import warnings
warnings.filterwarnings("ignore")

def SetupChrome():
    # set up chrome options
    global driver
    chrome_options = Options()

    # headless
    chrome_options.add_argument("--headless=new")    
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-notifications")

    # this is for docker
    chrome_options.add_argument('--disable-dev-shm-usage')        

    # full screen
    chrome_options.add_argument("--start-maximized")
    # set up driver
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)

    # go to linkedin
    driver.get('https://www.indeed.com/')
    return     


def ScrapJobCard(job_card):
    # click on the job card
    job_card.click()

    # sleep for a random amount of time between 1 and 3 seconds
    time.sleep(ceil(1 + 2 * random.random()))

    # wait for the job card to load
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//div[@class="jobsearch-embeddedBody css-1omm75o eu4oa1w0"]')))
    except:
        print('Cannot get this job description')
        return
    # title

    try:

        job_tilte = job_card.find_element(By.XPATH, './/h2').text
        print('title', job_tilte)

        # company name
        company_name = job_card.find_element(By.XPATH, './/div[@class="heading6 company_location tapItem-gutter companyInfo"]/span[@class="companyName"]')
        print('company', company_name.text)

        # job link by getting the current url
        job_link = job_card.find_element(By.XPATH, './/h2/a').get_attribute('href')
        print('link', job_link)

        # job description
        job_description = driver.find_element(By.XPATH, '//div[@class="jobsearch-embeddedBody css-1omm75o eu4oa1w0"]')
        print('description', job_description.text)


        # divider
        print("--------------------------------------------------")    

        # return the result
        return job_tilte, company_name.text, job_link, job_description.text

    except:
        print('Cannot get this job description')
        return
    
def WriteResultToCSV(df, job_title):
    # check if there is a folder called result
    try:
        df.to_csv(f'result/{job_title}.csv', index=False)

    except:
        # create a folder called result
        os.mkdir('result')

        # save the result
        df.to_csv(f'result/{job_title}.csv', index=False)

# main function
def main():

    job_titles = [
        # Analyzing Data
        "data scientist intern",
        "data intern",
        "business analyst intern",
        "data engineer intern",
        "quantitative analyst intern",
        "data analyst intern",
        
        # Working with Cloud and Building Cloud Architect
        "cloud architect intern",
        "cloud solutions intern",
        "cloud infrastructure architect intern",
        "cloud systems architect intern",
        "cloud engineer intern",
            
        # DevOps
        "devops engineer intern",
        "devops specialist intern",
        "devops architect intern",
    ]

    # set up chrome
    SetupChrome()

    # now go to each title in the list
    for job_title in job_titles[1:2]:

        # create a dataframe to store result
        df = pd.DataFrame(columns=['job_title', 'job_link', 'description', 'company_name'])

        # encoded the job title
        encoded_title = urllib.parse.quote(job_title)

        # the url
        main_url = f'https://www.indeed.com/jobs?q={encoded_title}&l=US&fromage=1'
        print(main_url) 

        # go to the url
        driver.get(main_url)

        # find the job list
        # use WebDriverWait to wait for the job list to load
        try:
            containers = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.XPATH, '//ul[@class="jobsearch-ResultsList css-0"]/li//tbody//td[@class="resultContent"]')))
        except:
            print("No job found")
            
            # write the result to a csv file
            WriteResultToCSV(df, job_title)            

            continue
        else:

            # loop through each job card
            for job_card in containers:
                # scrap the job card
                job_tilte, company_name, job_link, job_description = ScrapJobCard(job_card)

                # save the result to a csv file
                df = df.append({'job_title': job_tilte, 'job_link': job_link, 'description': job_description, 'company_name': company_name}, ignore_index=True)

            # save the result to a csv file
            WriteResultToCSV(df, job_title)
            

        # okay. Wait a random amount of time, between 10 and 30 seconds
        time.sleep(ceil(10 + 20 * random.random()))

    # close the driver
    driver.quit()
            
if __name__ == "__main__":
    main()
