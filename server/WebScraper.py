
# here i will explain what each import means

# theres an annoying message being printed, i will use os library to suppress that log later
import os

# we need a webdriver object from selenium library to do things like open the url
from selenium import webdriver 

# this import is needed because we want to fetch the links by the anchor tag <a>
from selenium.webdriver.common.by import By 

from selenium.webdriver.support.ui import WebDriverWait

from selenium.webdriver.support import expected_conditions as EC

from selenium.webdriver.common.alert import Alert

# this import is needed because we want to pause the page for 2 seconds when we load it so it loads fully
import time 

# we can use the standard list in python but i wanted to show return type of a function by -> List[str] for that i needed this
from typing import List 

# we need this to check if a url has different fqdn and also i wanted to check if two url are same with different identifier for page i.e. the #content thing
from urllib.parse import urlparse, urlunparse, parse_qs

# this it needed to run the breadth first search (bfs) on all the links
from collections import deque 

import requests

import config

import csv




# this class has all major functions related to web crawling
class WebScraper:




    # here in constructor i declare the different data structures that i will need and also declare the webdriver object
    def __init__(self, baseurl: str):

        # we need the base url to compare fqdn
        self.BaseUrl = baseurl

        # this set will keep track of all the links that have already been parsed so that we dont repeat anything
        self.parsed_links_set = set()

        # this is the selenium driver object for chrome. we will use this for all major crawling functions
        self.driver = webdriver.Chrome()

        # CSV file setup
        self.csv_file = "logs.csv"
        with open(self.csv_file, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(["Link", "HTTP Method", "Query Parameters", "Number of Parameters"])




    def close_alert(self):
        try:
            # Switch to alert and accept it (you can also use .dismiss() if you want to close it)
            alert = Alert(self.driver)
            alert.accept()
        except:
            # If no alert is present
            pass




    # Function to handle form authentication
    def handle_form_auth(self):
        try:
            # Find the form element
            forms = self.driver.find_elements(By.TAG_NAME, 'form')
            for form in forms:
                inputs = form.find_elements(By.TAG_NAME, 'input')
                filled = False
                
                for input_element in inputs:
                    input_type = input_element.get_attribute('type')
                    input_name = input_element.get_attribute('name')

                    # Populate input fields based on their type or name
                    if input_type in ["text", "email", "password", "tel"]:
                        value = config.PREDEFINED_VALUES.get(input_name)
                        if value:
                            input_element.clear()
                            input_element.send_keys(value)
                            filled = True

                if filled:
                    # Find the submit button and click it
                    submit_button = form.find_element(By.XPATH, ".//button[@type='submit'] | .//input[@type='submit']")
                    submit_button.click()
                    # print("Form submitted successfully!")
                    return
        except Exception as e:
            print(f"Error handling form authentication: {e}")




    # this function is called to open any url, and give it 2 seconds to load completely
    def open_page(self, url: str):
        try:

            response = requests.head(url, allow_redirects=True)

            if response.status_code == 401:
                auth_url = f"{urlparse(url).scheme}://{config.USERNAME}:{config.PASSWORD}@{urlparse(url).netloc}{urlparse(url).path}"
                self.driver.get(auth_url)
                # self.driver.get(url)
            else:
                self.driver.get(url)

            # # Close any alert pop-ups
            # self.close_alert()  

            # this is for me to see
            time.sleep(2)

            # # Attempt form authentication if forms are present
            self.handle_form_auth()

            time.sleep(2)

        except Exception as e:
            print(f"Exception occured while loading page: {e}")

    def log_link_details(self, url: str):
        try:
            # fetch HTTP methods
            response = requests.options(url)
            methods = response.headers.get('Allow', 'GET').split(',')

            # extract query parameters
            query_params = parse_qs(urlparse(url).query)
            formatter_params = ','.join([f"{key}={value}" for key, value in query_params.items()])
            num_params = len(query_params)

            # enter details into csv file
            for method in methods:
                with open(self.csv_file, mode='a', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    writer.writerow([url, method.strip(), formatter_params, num_params])
        except Exception as e:
            print(f"Error logging link details: {e}")        




    # this function is called from the main.py file when all the crawling has been done. it is good practice to close the driver as it frees the cpu and other resources. although the cpu is freed when the program ends
    def close_driver(self):
        self.driver.quit()




    # this function checks if the url has the same FQDN as the original base url or not
    def is_same_fqdn(self, url) -> bool:
        return urlparse(self.BaseUrl).netloc == urlparse(url).netloc




    # this function works independently of the crawler function. this returns a certain number of links that it can find using the anchor tag from the url the driver is currently on
    def get_links(self, limit: int = 10) -> List[str]:

        # the list to maintain the urls on current page
        extracted_links = []

        # finds all the objects with tag name as 'a' which stands for anchor tag. these arent strings yet
        links = self.driver.find_elements(By.TAG_NAME, 'a')

        # now we iterate over all anchor objects and get the href attribute, convert to string and store it in external links
        for link in links:

            # the href attribute of the anchor tag contains the link string
            raw_href = link.get_attribute('href')

            # if the href attribute is not null
            if raw_href:  
                # then parse it and remove the #/ identifier part because it basically is the same page
                href = urlunparse(urlparse(raw_href)._replace(fragment=""))

                # if something remains after removing the identifier part
                if href and self.is_same_fqdn(href):
                    # then append it to the list that we will return
                    extracted_links.append(href)

            # now if the size of the list exceeds the limit then we stop the loop and return the list
            if len(extracted_links) >= limit:
                break

        return extracted_links




    # this function uses bfs and the get_links() function to crawl to different pages from the base url. it only goes to a certain depht as specified
    def crawler(self, depth_limit:int = 3) :

        queue = deque([self.BaseUrl])

        # this variable is used to make sure the crawler stops at a certain depth
        current_depth = 0

        # logic here is a plain bfs
        while queue and current_depth <= depth_limit:
            
            # we iterate over all links at the current depth
            for _ in range(len(queue)):

                url = queue.popleft()
                print(url)

                if url in self.parsed_links_set:
                    continue

                self.log_link_details(url)
                self.parsed_links_set.add(url)
                self.open_page(url)

                new_links  = self.get_links()

                for link in new_links:

                    # we need to check again because we are getting all links from get_links() function which doesnt check for duplicates from the parsed_links_set
                    if link not in self.parsed_links_set:
                        queue.append(link)

            # after iterating all links at same depht, we increace this variable by one
            current_depth += 1







