import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from bs4 import BeautifulSoup
import time


DUMPS_ROOT_FOLDER = "marmoset_dump" # CONFIG

TARGET_MARMOSET_COURSE_PAGE = "https://marmoset.student.cs.uwaterloo.ca/"

def archive_project_submissions(driver, course_folder, project_name, submission_link):
    driver.get(f"https://marmoset.student.cs.uwaterloo.ca{submission_link}")
    html_content = driver.page_source
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Create folder for project submissions
    project_folder = os.path.join(course_folder, project_name)
    os.makedirs(project_folder, exist_ok=True)

    # Create CSV filename
    csv_file = os.path.join(project_folder, f"{project_name}_submissions.csv")

    # Find the submissions table
    submissions_table = soup.find('table')
    if submissions_table:
        # Check if CSV already exists
        if not os.path.exists(csv_file):
            # Open CSV file to write submission data
            with open(csv_file, 'w') as f:
                f.write("submission_id,submission_date,test_score\n")
                
                for row in submissions_table.find_all('tr')[1:]:  # Skip header row
                    cells = row.find_all('td')
                    if cells:
                        submission_id = cells[0].text.strip()  # First column is submission #
                        submission_date = cells[1].text.strip().replace(",", " ")  # Second column is date
                        test_score = cells[2].text.strip()  # Third column is test score

                        # Write to CSV
                        f.write(f"{submission_id},{submission_date},{test_score}\n")

        # Process downloads
        for row in submissions_table.find_all('tr')[1:]:  # Skip header row
            cells = row.find_all('td')
            if cells:
                submission_id = cells[0].text.strip()  # First column is submission #
                submission_date = cells[1].text.strip()  # Second column is date
                test_score = cells[2].text.strip()  # Third column is test score

                print(f"Scraping submission {submission_id} from {submission_date} with score {test_score}")

                # DETAILED SUBMISSION INFO
                # Create detailed test results folder
                detailed_test_results_folder = os.path.join(project_folder, f"detailed_test_results")
                os.makedirs(detailed_test_results_folder, exist_ok=True)

                if not os.path.exists(os.path.join(detailed_test_results_folder, f"{submission_id}.html")):
                    # Archive detailed test results
                    detailed_test_results_endpoint = cells[3].find('a')
                    # for some classes, the detailed test results endpoint is the 2nd last column
                    if not detailed_test_results_endpoint:
                        detailed_test_results_endpoint = cells[-2].find('a')['href']
                        if not detailed_test_results_endpoint:
                            print(f"No detailed test results endpoint found for submission {submission_id}")
                            continue
                    else:
                        detailed_test_results_endpoint = detailed_test_results_endpoint['href']
                    detailed_test_results_full_url = f"https://marmoset.student.cs.uwaterloo.ca{detailed_test_results_endpoint}"
                    driver.get(detailed_test_results_full_url)
                    detailed_test_results_html = driver.page_source
                    detailed_test_results_soup = BeautifulSoup(detailed_test_results_html, 'html.parser')

                    # Save HTML
                    with open(os.path.join(detailed_test_results_folder, f"submission_{submission_id}.html"), 'w') as f:
                        f.write(detailed_test_results_html)
                

                # DOWNLOAD SUBMISSION
                
                # Find download link in last column
                download_link = cells[-1].find('a')['href']
                full_download_link = f"https://marmoset.student.cs.uwaterloo.ca{download_link}"

                file_name = f"{project_name}_submission_{submission_id}.zip"
                downloaded_file = os.path.join(os.path.join(DUMPS_ROOT_FOLDER, "downloads"), f"{project_name}.zip")
                target_file = os.path.join(project_folder, file_name)

                # Check if the file already exists
                if os.path.exists(target_file):
                    print(f"Skipping {target_file} because it already exists")
                    continue
                
                # Download the submission
                driver.get(full_download_link)
                time.sleep(1)  # Wait for download to start
                
                print(f"Downloaded submission {submission_id} from {submission_date} with score {test_score}")
                
                # Wait for file to exist
                while not os.path.exists(downloaded_file):
                    print(f"Waiting for {downloaded_file} to exist")
                    time.sleep(0.5)
                    
                # Move file from downloads to target folder
                print(f"Moving {downloaded_file} to {target_file}")
                os.rename(downloaded_file, target_file)
                time.sleep(0.2)
                

def parse_course_page(driver):
    html_content = driver.page_source
    soup = BeautifulSoup(html_content, 'html.parser')

    course_name = soup.find('h1').find('a').text.strip()
    course_folder = os.path.join(DUMPS_ROOT_FOLDER, course_name)
    os.makedirs(course_folder, exist_ok=True)

    assessment_table = soup.find('table')
    if assessment_table:
        assessment_links = []
        for row in assessment_table.find_all('tr'):
            cells = row.find_all('td')
            if cells:  # Skip header row
                project_name = cells[0].find('a').text.strip()
                submission_link = cells[1].find('a')['href']
                assessment_links.append((project_name, submission_link))
                course_folder = os.path.join(DUMPS_ROOT_FOLDER, course_name)
                archive_project_submissions(driver, course_folder, project_name, submission_link)
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
    
    # Update these paths to match your actual Chrome profile location
    # Also make sure that the Chrome profile has UW password saved for easy ADFS click-through sequence
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
        "download.default_directory": os.path.join(os.path.abspath(DUMPS_ROOT_FOLDER), "downloads")
    }
    chrome_options.add_experimental_option("prefs", chrome_prefs)
    service = Service('/usr/bin/chromedriver')
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        # Create Course Folder
        root_dump_folder = os.path.abspath(DUMPS_ROOT_FOLDER)
        downloads_folder = os.path.join(root_dump_folder, "downloads")
        os.makedirs(root_dump_folder, exist_ok=True)
        os.makedirs(downloads_folder, exist_ok=True)

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
