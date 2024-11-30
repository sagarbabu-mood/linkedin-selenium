from flask import Flask, jsonify, request
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException, NoSuchElementException, ElementNotInteractableException
import time
import csv
import random
import os
from datetime import datetime

USERNAME = "abhinavp1902@gmail.com"
PASSWORD = "Abhi@2024"
CHROME_DRIVER_PATH = r"c:\Users\NxtWave Hire\Downloads\chromedriver-win32\chromedriver-win32\chromedriver.exe"
OUTPUT_DIRECTORY = r"C:\LA scrapping data\Linkedin"
LINK = "https://www.linkedin.com/jobs/search/?currentJobId=4072534283&f_E=1%2C2&f_TPR=r86400&keywords=python&origin=JOB_SEARCH_PAGE_JOB_FILTER&sortBy=DD"
KEYWORDS = [
    "Entry Level", "0", "0-1", "0-2", "Internship+ Full Time", "Internship",
    "2024", "2025", "2023", "Recent Graduates", "PPO", "JobOffer",
    "Trainee", "Intern", "0-3"
]
FRAUD_COMPANIES_LIST = ["Outscal Gaming", "turning", "Internkaksha IT Solutions",
                        "Truelancer.com", "Unified Mentor", "Uplers", "MedTourEasy"]
MAX_NO_OF_PAGES_TO_POOL = 3

app = Flask(__name__)

# Initialize the CSV file with headers


@app.route('/scrape-jobs', methods=['GET'])
def scrape_jobs():
    # Setup for the Chrome WebDriver

    chrome_options = Options()
    chrome_options.add_argument("--disable-webrtc")
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument(
        "--window-position=-3000,0")  # Move window off-screen
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--disable-popup-blocking")
    chrome_options.add_experimental_option(
        'excludeSwitches', ['enable-logging'])
    chrome_options.add_experimental_option('detach', True)
    chrome_options.add_argument("--window-size=1920,1080")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # Initialize job data list
    jobs_list = []

    # Initialize the CSV file
    csv_file_path = os.path.join(OUTPUT_DIRECTORY, 'jobs_list.csv')
    initialize_csv(csv_file_path)

    def account_login():
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "username")))
        print("logging into the Portal")
        # Enter the username
        username = driver.find_element(By.ID, "username")
        username.send_keys(USERNAME)  # Use constant from config
        print('sent username')
        # Enter the password
        password = driver.find_element(By.ID, "password")
        password.send_keys(PASSWORD)  # Use constant from config
        print('sent password')
        time.sleep(2)
        # Click the login button
        login_button = driver.find_element(
            By.XPATH, "//button[@type='submit']")
        login_button.click()
        print('login button clicked')

        WebDriverWait(driver, 10).until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, ".global-nav__me-photo")))
        print("accessing the profile image")

    def scroll_job_list():
        # Locate the child element with the correct class name for scrolling
        job_list = driver.find_element(
            By.CLASS_NAME, "YtCCjvwnvMFkeVBhkqvYpGiZrbLMCDAAWwk")
        num_elements_to_load = 3  # Number of elements to load with each scroll

        loaded_elements = len(driver.find_elements(
            By.CSS_SELECTOR, "[data-occludable-job-id]"))
        total_elements = loaded_elements + num_elements_to_load

        while loaded_elements < total_elements:
            print(
                f"Scrolling to load next {num_elements_to_load} job items...")

            # Scroll down a bit to load the next set of elements
            driver.execute_script(
                "arguments[0].scrollTop += arguments[0].offsetHeight;", job_list)
            time.sleep(2)  # Allow time for the elements to load

            new_loaded_elements = len(driver.find_elements(
                By.CSS_SELECTOR, "[data-occludable-job-id]"))

            if new_loaded_elements == loaded_elements:
                print("No more new elements loaded.")
                break  # Stop if no new elements are being loaded
            else:
                print(
                    f"Loaded {new_loaded_elements - loaded_elements} new job items.")
                loaded_elements = new_loaded_elements

    def extract_job_details():
        wait_time = random.randint(1, 3)
        time.sleep(wait_time)

        main_container = driver.find_element(
            By.CLASS_NAME, "jobs-search__job-details--wrapper")

        # Extract Job Title
        try:
            title = main_container.find_element(
                By.CSS_SELECTOR, "h1.t-24.t-bold.inline a").text
        except:
            title = "NA"

        # Extract Job Link
        try:
            job_title_element = main_container.find_element(
                By.CSS_SELECTOR, "div.t-24.job-details-jobs-unified-top-card__job-title h1 a")
            job_link = job_title_element.get_attribute("href")
        except:
            job_link = "NA"

        # Extract Company Name
        try:
            company = main_container.find_element(
                By.CLASS_NAME, "job-details-jobs-unified-top-card__company-name").text
        except:
            company = "NA"

        # Extract Location and Posted Time
        try:
            primary_description_container = main_container.find_element(
                By.CLASS_NAME, "job-details-jobs-unified-top-card__primary-description-container")
            primary_description_text = primary_description_container.text
            parts = primary_description_text.split(' · ')

            if len(parts) >= 2:
                location = parts[0].strip()
                posted_time = parts[1].strip()
            else:
                location = "NA"
                posted_time = "NA"
        except Exception as e:
            location = "NA"
            posted_time = "NA"
            0
        try:
            job_insight_element = driver.find_element(
                By.CLASS_NAME, "job-details-preferences-and-skills")
            insight_text = job_insight_element.text
        except NoSuchElementException:
            insight_text = "NA"

        # Extract Job Description
        try:
            job_description_element = driver.find_element(
                By.CSS_SELECTOR, "div.jobs-box__html-content.jobs-description-content__text--stretch")
            job_description = job_description_element.text.strip()
        except:
            job_description = "NA"

        # Track matched keywords, allowing partial matches for all except "PPO"
        matched_keywords = []

        for keyword in KEYWORDS:
            if keyword.lower() in ["ppo", "intern", "internship", "interns"]:
                # Exact match check for "PPO" (case insensitive)
                if any(f" {keyword.lower()} " in f" {detail.lower()} " for detail in [job_description, title, company]):
                    matched_keywords.append(keyword)
            else:
                # Partial match for other keywords (case insensitive)
                if any(keyword.lower() in detail.lower() for detail in [job_description, title, company]):
                    matched_keywords.append(keyword)

        matched_keywords_str = ', '.join(
            matched_keywords) if matched_keywords else "None"

        print(f"Title: {title}")
        print(f"Company: {company}")
        print(f"Location: {location}")
        print(f"Posted Time: {posted_time}")
        print(f"Job Details: {insight_text}")
        print(f"Job Description: {job_description}")
        print(f"Job Link: {job_link}")
        print(f"Matched Keywords: {matched_keywords_str}")

        job_details = {
            "Title": title,
            "Company": company,
            "Posted Time": posted_time,
            "Location": location,
            "Job Link": job_link,
            "Job Details": insight_text,
            "Job Description": job_description,
            "Matched Keywords": matched_keywords_str
        }

        # Append the job details to the CSV file
        append_to_csv(csv_file_path, job_details)

    def click_each_job_item():
        job_items = driver.find_elements(
            By.CSS_SELECTOR, '[data-occludable-job-id]')

        for job in job_items:
            # Check if the job has already been viewed
            try:
                viewed_label = job.find_element(
                    By.CSS_SELECTOR, "li.job-card-container__footer-item.job-card-container__footer-job-state.t-bold")
                if "Viewed" in viewed_label.text:
                    print("Job already viewed. Skipping this job item.")
                    continue  # Skip to the next job item
            except NoSuchElementException:
                # If the 'Viewed' label is not present, proceed to click the job
                pass

            # Extract the company name before clicking the job item
            try:
                company_element = job.find_element(
                    By.CLASS_NAME, 'job-card-container__primary-description')
                company_name = company_element.text.strip()

                # Check if the company is in the fraud list (case insensitive)
                if company_name.lower() in [fraud_company.lower() for fraud_company in FRAUD_COMPANIES_LIST]:
                    print(
                        f"Skipping job from fraudulent company: {company_name}")
                    continue  # Skip this job and move to the next one

            except NoSuchElementException:
                print("Company name element not found. Proceeding with caution...")

            wait_time = random.randint(2, 4)
            print(
                f"Waiting for {wait_time} seconds before clicking the next job...")
            time.sleep(wait_time)
            scroll_job_list()

            try:
                job_link = job.find_element(
                    By.CSS_SELECTOR, 'a.job-card-container__link')
                job_link.click()
                print("Clicked job item and extracting the job details")
                extract_job_details()
            except (ElementNotInteractableException, NoSuchElementException):
                print("Anchor element not clickable. Trying a different element...")
                # Try to click another element
                alternative_links = driver.find_elements(
                    By.CSS_SELECTOR, 'a.job-card-container__link')
                if alternative_links:
                    alternative_links[0].click()
                    print(
                        "Clicked an alternative job item and extracting the job details")
                    extract_job_details()
                else:
                    print("No alternative job elements found.")

    def get_job_listings():
        try:
            # Wait for the job list container to be present
            job_list_container = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located(
                    (By.CLASS_NAME, "scaffold-layout__list"))
            )
            print("Job list container found.")

            # Find all job listings on the page
            job_list_items = job_list_container.find_elements(
                By.CSS_SELECTOR, "[data-occludable-job-id]")
            print(
                f"Total number of job listings on the page: {len(job_list_items)}")

            # Process each job item
            click_each_job_item()

        except TimeoutException as e:
            print("Job list container not found or took too long to load.", str(e))
        except NoSuchElementException as e:
            print("Error accessing job listing details.", str(e))
        except Exception as e:
            print("An error occurred:", str(e))

    def click_next_button(current_page):
        try:
            # Construct the aria-label for the next page
            next_page_label = f"Page {current_page + 1}"

            # Find the button for the next page
            next_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable(
                    (By.XPATH, f"//ul/li/button[@aria-label='{next_page_label}']"))
            )
            next_button.click()
            print(f"Next button for {next_page_label} clicked.")
            return True
        except TimeoutException:
            print(f"Next button for {next_page_label} not found.")
            return False

    def iterate_pages():
        page = 1
        max_pages = MAX_NO_OF_PAGES_TO_POOL
        while page <= max_pages:
            print(f"Extracting jobs from page {page}")
            get_job_listings()

            if click_next_button(page):
                wait_time = random.randint(2, 3)
                print(
                    f"Waiting for {wait_time} seconds before moving to the next page...")
                time.sleep(wait_time)
                page += 1
            else:
                print("No more pages. Extraction complete.")
                break

    try:
        # Call your scraping function here
        driver.get("https://www.linkedin.com/login")
        print("Navigated to LinkedIn login page.")
        account_login()
        print("Login function completed successfully.")
        driver.get(LINK)
        iterate_pages()
    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        driver.quit()

    # Save the data to CSV or return JSON
    return jsonify(jobs_list)


if __name__ == '__main__':
    app.run(debug=True)
