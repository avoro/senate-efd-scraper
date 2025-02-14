import unittest
from unittest.mock import patch, MagicMock
import json
import os
from src.senate_scraper import SenateScraper
from selenium.common.exceptions import TimeoutException


class TestSenateScraper(unittest.TestCase):
    def setUp(self):
        """Set up test cases."""
        self.patcher = patch("selenium.webdriver.Chrome")
        self.mock_driver = self.patcher.start()
        self.scraper = SenateScraper(headless=True)

    def tearDown(self):
        """Clean up after tests."""
        self.patcher.stop()

    def test_init(self):
        """Test SenateScraper initialization."""
        self.assertIsNotNone(self.scraper.driver)
        self.assertIsNone(self.scraper.email_client)

    @patch("selenium.webdriver.support.wait.WebDriverWait")
    @patch("selenium.webdriver.support.expected_conditions.element_to_be_clickable")
    @patch("time.sleep")
    def test_accept_agreement_success(self, mock_sleep, mock_ec, mock_wait):
        """Test successful agreement acceptance."""
        # Create mock checkbox
        mock_checkbox = MagicMock()
        mock_checkbox.is_selected.return_value = False

        # Setup the condition to return our mock checkbox
        mock_ec.return_value = lambda driver: mock_checkbox

        # Setup WebDriverWait
        mock_wait_instance = MagicMock()
        mock_wait.return_value = mock_wait_instance
        mock_wait_instance.until.side_effect = lambda condition: condition(None)

        # Test
        result = self.scraper.accept_agreement()

        # Assertions
        self.assertTrue(result)
        mock_checkbox.click.assert_called_once()
        mock_sleep.assert_called_once_with(3)

    @patch("selenium.webdriver.support.ui.WebDriverWait")
    def test_accept_agreement_timeout(self, mock_wait):
        """Test agreement acceptance with timeout."""
        # Setup
        mock_wait.return_value.until.side_effect = TimeoutException()

        # Test
        result = self.scraper.accept_agreement()

        # Assert
        self.assertFalse(result)

    def test_navigate_to_search_success(self):
        """Test successful navigation to search page."""
        result = self.scraper.navigate_to_search()
        self.assertTrue(result)
        self.scraper.driver.get.assert_called_once()

    def test_navigate_to_search_failure(self):
        """Test failed navigation to search page."""
        self.scraper.driver.get.side_effect = Exception("Test error")
        result = self.scraper.navigate_to_search()
        self.assertFalse(result)

    def test_save_reports_to_json(self):
        """Test saving reports to JSON file."""
        # Test data
        test_reports = [{"test": "data"}]
        filename = "test_reports.json"

        try:
            # Test
            result = self.scraper.save_reports_to_json(test_reports, filename)

            # Assert
            self.assertIsNotNone(result)
            self.assertTrue(os.path.exists(filename))

            # Verify content
            with open(filename, "r", encoding="utf-8") as f:
                saved_data = json.load(f)
            self.assertEqual(saved_data, test_reports)

        finally:
            # Cleanup
            if os.path.exists(filename):
                os.remove(filename)

    def test_check_empty_results_true(self):
        """Test empty results check when results are empty."""
        mock_element = MagicMock()
        self.scraper.driver.find_elements.return_value = [mock_element]
        result = self.scraper.check_empty_results()
        self.assertTrue(result)

    def test_check_empty_results_false(self):
        """Test empty results check when results exist."""
        self.scraper.driver.find_elements.return_value = []
        result = self.scraper.check_empty_results()
        self.assertFalse(result)

    @patch("src.senate_scraper.EmailClient")
    def test_send_notification(self, mock_email_client):
        """Test sending notification."""
        # Setup
        test_subject = "Test Subject"
        test_body = "Test Body"
        mock_email_client_instance = MagicMock()
        self.scraper.email_client = mock_email_client_instance

        # Test
        self.scraper.send_notification(test_subject, test_body)

        # Assert
        mock_email_client_instance.send_email.assert_called_once()

    def test_extract_report_urls(self):
        """Test extracting report URLs."""
        # Setup
        mock_tbody = MagicMock()
        mock_link1 = MagicMock()
        mock_link1.get_attribute.return_value = "http://test1.com"
        mock_link2 = MagicMock()
        mock_link2.get_attribute.return_value = "http://test2.com"
        mock_tbody.find_elements.return_value = [mock_link1, mock_link2]
        self.scraper.driver.find_element.return_value = mock_tbody

        # Test
        urls = self.scraper.extract_report_urls()

        # Assert
        self.assertEqual(len(urls), 2)
        self.assertEqual(urls[0], "http://test1.com")
        self.assertEqual(urls[1], "http://test2.com")


if __name__ == "__main__":
    unittest.main()
