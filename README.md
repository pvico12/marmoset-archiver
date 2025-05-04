# Marmoset Archiver

## Overview
This script automates the process of archiving all your Marmoset submissions for a given course. Marmoset is a submission and testing server used at the University of Waterloo for programming assignments. This script provides several key benefits:

1. **Complete Submission History**: Downloads all your past submissions for each project in the course
2. **Submission Metadata**: Creates CSV files containing detailed information about each submission, including:
   - Submission ID
   - Submission date and time
   - Test scores
3. **Organized Storage**: Creates a structured folder hierarchy:
   ```
   marmoset_dump/
   ├── course_name/
   │   ├── project1/
   │   │   ├── project1_submissions.csv
   │   │   ├── project1_submission_1.zip
   │   │   ├── project1_submission_2.zip
   │   │   └── ...
   │   ├── project2/
   │   └── ...
   └── downloads/
   ```

This archival system is particularly useful for:
- Keeping a personal backup of all your submissions
- Reviewing your submission history and progress
- Having access to your code even after the course ends
- Analyzing your test score improvements over time

## Configuration
Set any of these 3 variables to match your setup.
```
DUMPS_ROOT_FOLDER = "marmoset_dump"
TARGET_MARMOSET_COURSE_PAGE = "https://marmoset.student.cs.uwaterloo.ca/marmoset-w23-f23/" (there are many different marmoset endpoints depending on years)
user_data_dir = "/home/pvico/.config/google-chrome"
profile_directory = "Default"
```
**Note**: Your chrome instance that the chrome driver will use (see more below) needs to be logged into a profile that has logged in to Crowdmark already and persisted a session. This script does not handle Crowdmark login due to the several different login types based on your school.

## Requirements
### Install Chrome
```
sudo apt-get update
sudo apt-get install -y curl unzip xvfb libxi6 libgconf-2-4
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo apt install ./google-chrome-stable_current_amd64.deb
google-chrome --version
```

### Install ChromeDriver
```
wget https://storage.googleapis.com/chrome-for-testing-public/135.0.7049.84/linux64/chromedriver-linux64.zip
unzip chromedriver-linux64.zip
sudo mv chromedriver-linux64/chromedriver /usr/bin/chromedriver
sudo chown root:root /usr/bin/chromedriver
sudo chmod +x /usr/bin/chromedriver
```



