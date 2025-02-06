import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from typing import List, Optional, Dict, Any
import time
from datetime import datetime
import json

# Module level constants
TIMEOUT = 10
BASE_URL = "https://efdsearch.senate.gov/search/"

# Configure basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SenateScraper:
    """A class to scrape financial disclosure data from the Senate website."""

    def __init__(self, headless: bool = True):
        """
        Initialize the scraper with configuration.

        Args:
            headless (bool): Whether to run browser in headless mode
        """
        logger.info("Initializing SenateScraper...")
        self.driver = self._setup_driver(headless)

    def _setup_driver(self, headless: bool) -> webdriver.Chrome:
        """
        Set up and configure Chrome WebDriver.

        Args:
            headless (bool): Whether to run browser in headless mode

        Returns:
            webdriver.Chrome: Configured Chrome WebDriver instance
        """
        options = webdriver.ChromeOptions()
        if headless:
            options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')

        return webdriver.Chrome(options=options)

    def navigate_to_search(self) -> bool:
        """
        Navigate to the search page.

        Returns:
            bool: True if navigation was successful, False otherwise
        """
        try:
            logger.info(f"Navigating to {BASE_URL}")
            self.driver.get(BASE_URL)
            return True

        except Exception as e:
            logger.error(f"Error navigating to search page: {str(e)}")
            return False

    def accept_agreement(self) -> bool:
        """
        Accept the agreement by clicking the checkbox and wait for next page.

        Returns:
            bool: True if agreement was accepted successfully, False otherwise
        """
        try:
            logger.info("Attempting to click agreement checkbox")
            agreement_checkbox = WebDriverWait(self.driver, TIMEOUT).until(
                EC.element_to_be_clickable((By.ID, "agree_statement"))
            )
            if not agreement_checkbox.is_selected():
                agreement_checkbox.click()
                logger.info("Successfully clicked agreement checkbox")

            # Wait for page to load
            time.sleep(3)  # Wait for 3 seconds
            logger.info("Waited for page load")

            return True

        except TimeoutException:
            logger.error("Timeout while waiting for agreement checkbox")
            return False
        except Exception as e:
            logger.error(f"Error accepting agreement: {str(e)}")
            return False

    def fill_search_form(self) -> bool:
        """
        Fill out and submit the search form with specified criteria.

        Returns:
            bool: True if form was submitted successfully, False otherwise
        """
        try:
            logger.info("Filling out search form")

            # Select report type checkbox for Periodic Transactions
            report_checkbox = WebDriverWait(self.driver, TIMEOUT).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "input[id='reportTypes'][value='11']"))
            )
            if not report_checkbox.is_selected():
                report_checkbox.click()
                logger.info("Selected Periodic Transactions checkbox")

            # Enter today's date
            today_date = datetime.now().strftime("%m/%d/%Y")
            date_input = WebDriverWait(self.driver, TIMEOUT).until(
                EC.presence_of_element_located((By.ID, "fromDate"))
            )
            date_input.send_keys(today_date)
            logger.info(f"Entered date: {today_date}")

            # Click search button
            search_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            search_button.click()
            logger.info("Clicked search button")

            # Wait for results page
            time.sleep(3)
            logger.info("Waited for search results")

            return True

        except TimeoutException:
            logger.error("Timeout while filling search form")
            return False
        except Exception as e:
            logger.error(f"Error filling search form: {str(e)}")
            return False

    def check_empty_results(self) -> bool:
        """
        Check if the search returned no results.

        Returns:
            bool: True if no results were found, False otherwise
        """
        try:
            empty_results = self.driver.find_elements(By.CLASS_NAME, "dataTables_empty")
            if empty_results:
                logger.info("No reports found for today")
                return True
            return False

        except Exception as e:
            logger.error(f"Error checking results: {str(e)}")
            return False

    def extract_report_urls(self) -> List[str]:
        """
        Extract URLs for all report links from the results table.

        Returns:
            List[str]: List of report URLs found
        """
        try:
            logger.info("Starting to extract report URLs from results table")
            urls = []

            # Find the tbody element
            tbody = self.driver.find_element(By.TAG_NAME, "tbody")
            # Find all links within the tbody
            links = tbody.find_elements(By.TAG_NAME, "a")

            for link in links:
                url = link.get_attribute('href')
                if url:
                    urls.append(url)
                    logger.info(f"Found report URL: {url}")

            logger.info(f"Extracted {len(urls)} report URLs")
            return urls

        except Exception as e:
            logger.error(f"Error extracting report URLs: {str(e)}")
            return []

    def process_single_report(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Process a single report URL and extract relevant information.

        Args:
            url (str): URL of the report to process

        Returns:
            Optional[Dict[str, Any]]: Dictionary containing extracted information or None if extraction fails
        """
        try:
            logger.info(f"Processing report at URL: {url}")
            self.driver.get(url)

            # Wait for the page to load
            time.sleep(3)

            # Extract basic information
            report_data = {
                "url": url,
                "timestamp": datetime.now().isoformat(),
                "transactions": []
            }

            # Wait for and extract the transactions table
            table = WebDriverWait(self.driver, TIMEOUT).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "table.table"))
            )

            # Extract table rows (skip header row)
            rows = table.find_elements(By.TAG_NAME, "tr")[1:]

            for row in rows:
                cells = row.find_elements(By.TAG_NAME, "td")
                if len(cells) >= 9:  # Ensure we have all columns
                    transaction = {
                        "number": cells[0].text.strip(),
                        "transaction_date": cells[1].text.strip(),
                        "owner": cells[2].text.strip(),
                        "ticker": cells[3].text.strip(),
                        "asset_name": cells[4].text.strip(),
                        "asset_type": cells[5].text.strip(),
                        "type": cells[6].text.strip(),
                        "amount": cells[7].text.strip(),
                        "comment": cells[8].text.strip()
                    }
                    report_data["transactions"].append(transaction)
                    logger.info(f"Extracted transaction: {transaction}")

            return report_data

        except TimeoutException:
            logger.error(f"Timeout while processing report at {url}")
            return None
        except Exception as e:
            logger.error(f"Error processing report at {url}: {str(e)}")
            return None

    def process_all_reports(self, report_urls: List[str]) -> List[Dict[str, Any]]:
        """
        Process all report URLs and collect their information.

        Args:
            report_urls (List[str]): List of report URLs to process

        Returns:
            List[Dict[str, Any]]: List of dictionaries containing extracted information
        """
        all_reports = []

        for i, url in enumerate(report_urls, 1):
            logger.info(f"Processing report {i} of {len(report_urls)}: {url}")
            report_data = self.process_single_report(url)
            if report_data:
                all_reports.append(report_data)

        return all_reports

    def save_reports_to_json(self, reports: List[Dict[str, Any]], filename: str = None) -> bool:
        """
        Save the collected reports to a JSON file with the current date.

        Args:
            reports (List[Dict[str, Any]]): List of report dictionaries to save
            filename (str, optional): Name of the output JSON file. If None, generates with date

        Returns:
            bool: True if save was successful, False otherwise
        """
        if filename is None:
            today = datetime.now().strftime("%Y-%m-%d")
            filename = f"senate_reports_{today}.json"
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(reports, f, indent=2, ensure_ascii=False)
            logger.info(f"Successfully saved reports to {filename}")
            return True
        except Exception as e:
            logger.error(f"Error saving reports to JSON: {str(e)}")
            return False

    def cleanup(self) -> None:
        """Clean up resources."""
        logger.info("Cleaning up resources...")
        if hasattr(self, 'driver'):
            self.driver.quit()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.cleanup()
        if exc_type is not None:
            logger.error(f"Error occurred: {str(exc_val)}")
            return False
        return True


if __name__ == "__main__":
    try:
        with SenateScraper(headless=False) as scraper:
            if scraper.navigate_to_search() and scraper.accept_agreement():
                logger.info("Successfully initialized search page")
                if scraper.fill_search_form():
                    logger.info("Successfully submitted search form")
                    if scraper.check_empty_results():
                        logger.info("Exiting as no reports were found")
                        exit(0)

                    # Extract report URLs if results exist
                    report_urls = scraper.extract_report_urls()
                    if not report_urls:
                        logger.error("Failed to extract any report URLs")
                        exit(1)

                    logger.info(f"Successfully extracted {len(report_urls)} report URLs")

                    # Process all reports and save to JSON
                    all_reports = scraper.process_all_reports(report_urls)
                    if all_reports:
                        scraper.save_reports_to_json(all_reports)
                        logger.info("Successfully completed report processing")
                    else:
                        logger.error("No reports were successfully processed")
                        exit(1)

    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        exit(1)