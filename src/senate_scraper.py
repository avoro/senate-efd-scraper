import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from typing import List, Optional
import time
from datetime import datetime

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

            # Select report type checkbox
            report_checkbox = WebDriverWait(self.driver, TIMEOUT).until(
                EC.element_to_be_clickable((By.ID, "reportTypes"))
            )
            if not report_checkbox.is_selected():
                report_checkbox.click()
                logger.info("Selected report type checkbox")

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
                    # Add next steps here

    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")