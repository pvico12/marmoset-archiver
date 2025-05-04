import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from bs4 import BeautifulSoup
import time

TARGET_MARMOSET_COURSE_PAGE = "https://marmoset.student.cs.uwaterloo.ca/marmoset-w23-f23/"

def parse_course_page(driver):
    html_content = driver.page_source
    soup = BeautifulSoup(html_content, 'html.parser')
    assessment_table = soup.find('table')
    if assessment_table:
        assessment_links = []
        for row in assessment_table.find_all('tr'):
            cells = row.find_all('td')
            if cells:  # Skip header row
                project_name = cells[0].find('a').text.strip()
                submission_link = cells[1].find('a')['href']
                assessment_links.append((project_name, submission_link))
        return assessment_links

def parse_course_list_page(driver):
    html_content = driver.page_source
    soup = BeautifulSoup(html_content, 'html.parser')
    course_list = soup.find('ul')
    course_links = []
    if course_list:
        for row in course_list.find_all('li'):
            course_links.append(row.find('a')['href'])
    return course_links
    
def authenticate_marmoset_homepage(driver):
    # Click input tag with type "submit" and value "as"
    submit_button = driver.find_element(By.XPATH, "//input[@type='submit' and @value='as']")
    submit_button.click()

    time.sleep(2)

def uw_authenticated(html_content):
    # If there is "Sign in with username@uwaterloo.ca" on the page, then we are not logged in
    if "Sign in with username@uwaterloo.ca" in html_content:
        return False
    else:
        return True
    
def login_to_uw_auth(driver):
    # Click "Next" button
    next_button = driver.find_element(By.ID, "nextButton")
    next_button.click()

    time.sleep(2)

    # Click "Sign in" button
    sign_in_button = driver.find_element(By.ID, "submitButton")
    sign_in_button.click()

    time.sleep(2)
    
    
def at_marmoset_home_page(html_content):
    # If there is "Current Marmoset courses" on the page, then we are at the home page
    if "Welcome to the Marmoset Submit and Testing Server" in html_content:
        return True
    else:
        return False
    
def get_marmoset_page_type(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    h2_tag = soup.find('h2')
    has_projects_h2 = h2_tag and "Projects" in h2_tag.text
    
    if "All Courses" in html_content:
        return "course_list"
    elif has_projects_h2:
        return "course" 
    else:
        return "unknown"

if __name__ == "__main__":
    dumps_root_folder = "marmoset_dump" # CONFIG
    
    # Update these paths to match your actual Chrome profile location
    # Also make sure that the Chrome profile already is logged into a Marmoset session
    user_data_dir = "/home/user/.config/google-chrome" # CONFIG
    profile_directory = "Default" # CONFIG
    
    # Set up Selenium with headless mode and PDF printing
    chrome_options = Options()
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--enable-print-browser")
    chrome_options.add_argument(f"--user-data-dir={user_data_dir}")
    chrome_options.add_argument(f"--profile-directory={profile_directory}")
    chrome_options.add_argument("--kiosk-printing")  # Enables silent printing
    chrome_prefs = {
        "printing.print_preview_sticky_settings.appState": '{"recentDestinations":[{"id":"Save as PDF","origin":"local"}],"selectedDestinationId":"Save as PDF","version":2}',
        "savefile.default_directory": os.path.abspath(dumps_root_folder)
    }
    chrome_options.add_experimental_option("prefs", chrome_prefs)
    service = Service('/usr/bin/chromedriver')
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        # Create Course Folder
        # course_folder = os.path.join(dumps_root_folder, TARGET_COURSE_NAME)
        # os.makedirs(course_folder, exist_ok=True)

        # Get Target Marmoset Course Page
        driver.get(TARGET_MARMOSET_COURSE_PAGE)
        html_content = driver.page_source
        time.sleep(5)

        # Check if we are logged in
        if not uw_authenticated(html_content):
            print("Not logged in, logging in...")
            login_to_uw_auth(driver)
            time.sleep(5)
        html_content = driver.page_source
        
        # Check if we are at the Marmoset Home Page
        if at_marmoset_home_page(html_content):
            print("At Marmoset Home Page, authenticating...")
            authenticate_marmoset_homepage(driver)
        html_content = driver.page_source

        # Check Marmoset Page Type
        marmoset_page_type = get_marmoset_page_type(html_content)
        if marmoset_page_type == "unknown":
            print("Unknown Marmoset Page Type, exiting...")
            exit()
            
        elif marmoset_page_type == "course":
            print("At Marmoset Course Page, getting assessment links...")
            parse_course_page(driver)            
            
        elif marmoset_page_type == "course_list":
            print("At Marmoset Project Page, getting project links...")
            course_links = parse_course_list_page(driver)
            for course_link in course_links:
                driver.get(f"https://marmoset.student.cs.uwaterloo.ca{course_link}")
                html_content = driver.page_source
                parse_course_page(driver)
                time.sleep(5)



    finally:
        driver.quit()
