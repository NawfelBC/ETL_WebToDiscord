import requests
from bs4 import BeautifulSoup as bs
from selenium import webdriver
from time import sleep
import os
import pyrebase
from dotenv import load_dotenv, find_dotenv

FirebaseConfig ={"apiKey": os.getenv('API_KEY'),
"authDomain": os.getenv('AUTH_DOMAIN'),
"databaseURL": os.getenv('DB_URL'),
"projectId": os.getenv('PROJECT_ID'),
"storageBucket": os.getenv('STORAGE_BUCKET'),
"messagingSenderId": os.getenv('SENDER_ID'),
"appId": os.getenv('APP_ID'),
"measurementId": os.getenv('MEASUREMENT_ID')}

firebase = pyrebase.initialize_app(FirebaseConfig)

db = firebase.database()

def scraper():
    while True:
        jobs_list = []
        links_list = []

        chrome_options = webdriver.ChromeOptions()
        chrome_options.binary_location = os.environ.get('GOOGLE_CHROME_BIN')
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--no-sandbox')

        driver = webdriver.Chrome(executable_path=os.environ.get('CHROMEDRIVER_PATH'), options=chrome_options)
        

        URL = 'https://swissdevjobs.ch/fr'
        driver.get(URL)
        print('Opening Site')
        sleep(2)
        driver.find_element_by_xpath('//*[@id="root"]/div/div[1]/article/div/div[1]/div[1]/div[2]/button').click()
        sleep(1)
        driver.find_element_by_xpath('//*[@id="root"]/div/div[1]/article/div/div[1]/div[1]/div[6]/div/div/div[2]/div[3]/div[3]/div[2]/div[5]').click()
        sleep(1)
        driver.find_element_by_xpath('//*[@id="root"]/div/div[1]/article/div/div[1]/div[1]/div[6]/div/div/div[3]/button[2]').click()
        html = driver.page_source
        driver.close()
        soup = bs(html, "html.parser")
        
        jobs = soup.find_all('div', class_ = 'black-text cut-long-name font-weight-bold')
        salaries = soup.find_all('div', class_ = 'green-text mb-2')
        links = soup.find_all('a', target = '_self')
        for link in links:
            if '/fr/jobs/' in link['href']:
                links_list.append('https://www.swissdevjobs.ch' + link['href'])
        links_list.append('')
        links_list = list(dict.fromkeys(links_list))

        for (job,salary, link_) in zip(jobs,salaries,links_list):
            jobs_list.append((job.getText(), link_, salary.getText().replace('\xa0','').replace('❖','').replace('’','.')))
        
        jobs_list.pop(len(jobs_list)-1)

        jobs_firebase = db.child('Jobs').get()
        values = jobs_firebase.val()
        temp = []

        for item in values:
            temp.append((item['job'],item['link'],item['salary']))


        if temp != jobs_list:
            print('New Job found !')
            new_jobs = [x for x in jobs_list if x not in temp]

            print('Posting to Discord !')
            for i in range(len(new_jobs)):
                post_discord(new_jobs[i][0],new_jobs[i][2],new_jobs[i][1])
                sleep(2)
            
            data = {}
            collection = []
            for i in range(len(jobs_list)):
                data = {"job":jobs_list[i][0], "link":jobs_list[i][1], "salary":jobs_list[i][2]}
                collection.append(data)
    
            db.child("Jobs").set(collection)
            print('Database updated !')

        print('Going to sleep for 2 hours ...')
        sleep(7200)
        

def post_discord(job,salary,link):

    payload = {
        'content': f'Job : {job}\nSalary : {salary}\nLink : {link}\n '
    }

    header = {
        'authorization': os.getenv('AUTHORIZATION')
    }

    r = requests.post(os.getenv('CHANNEL_LINK'), data=payload, headers=header)

if __name__ == '__main__':
    scraper()