# Senate Financial Disclosure Scraper

A Python-based web scraper that automatically retrieves and processes financial disclosure reports from the U.S. Senate website, with email notification capabilities.

## Features

- Automated navigation and form submission on the Senate financial disclosure website
- Extraction of transaction data from periodic transaction reports (PTRs)
- Email notifications for successful runs and errors
- JSON export of scraped data
- Configurable headless browser operation
- Automated report attachment to notification emails

## Prerequisites

- Python 3.8+
- Gmail account (for notifications)

Note: Selenium will automatically handle the installation and management of Chrome and ChromeDriver.

## Installation

1. Clone the repository:
```bash
git clone https://github.com/avoro/senate-efd-scraper.git
cd senate-disclosure-scraper
```

2. Install required packages:
```bash
source venv/bin/activate
```

3. Set up environment variables by creating a `.env` file in the project root:
```plaintext
GMAIL_EMAIL=your.email@gmail.com
GMAIL_PASSWORD=your-app-specific-password
```

Note: For Gmail, you'll need to use an App Password rather than your regular password.

## Usage

Run the scraper:
```bash
python src/senate_scraper.py
```

The scraper will:
1. Navigate to the Senate Financial Disclosures website
2. Accept the agreement
3. Search for today's periodic transaction reports
4. Extract and process any found reports
5. Save the data to a JSON file
6. Send an email notification with the report attached

## Email Notifications

The system sends three types of email notifications:
1. Success notifications with the JSON report attached
2. "No Reports" notifications when no new reports are found
3. Error notifications if something goes wrong during execution

## Configuration Options

In `senate_scraper.py`:
- `TIMEOUT`: Configure wait times for page elements (default: 10 seconds)
- `headless`: Set to True/False for headless browser operation

In `email_client.py`:
- `smtp_server`: SMTP server address (default: smtp.gmail.com)
- `smtp_port`: SMTP port (default: 587)

## Security Notes

1. Never commit your `.env` file to version control
2. Use App Passwords for Gmail authentication