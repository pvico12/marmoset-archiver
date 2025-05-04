# Crowdmark Scraper

## Overview
This script will scrape all Crowdmark assignments and exams from current AND archived courses, and download them all as PDFs locally.

## Configuration
Set any of these 3 variables to match your setup.
```
dumps_root_folder = "scraper-dump"
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



