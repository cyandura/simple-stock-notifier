# simple-stock-notifier
Runs on a schedule to check a website for an element’s text and sends an SMS (Twilio) when it differs from the expected string.

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Install a browser for Playwright (one-time). The script uses a headless browser so the site sees real JavaScript and cookies instead of a "enable JavaScript and cookies" block:
   ```bash
   ./venv\Scripts\activate.bat
   py -m pip install -r requirements.txt
   playwright install chromium
   ```
   On Linux you may need system libs: `playwright install-deps`

3. Set environment variables or secrets that are required for running. This is the python command that is ran
   ```bash
   python check_website.py -- \
            "${{ secrets.WEBSITE_URL }}" \
            "${{ vars.WEBSITE_HTML_SELECTOR }}" \
            "${{ vars.WEBSITE_EXPECTED_TEXT }}" \
            "${{ secrets.GMAIL_APP_PASSWORD }}" \
            "${{ secrets.SMS_RECIPIENTS_AND_CARRIERS }}" \
            "${{ secrets.TELEGRAM_BOT_TOKEN }}" \
            "${{ secrets.TELEGRAM_CHAT_ID }}"
   ```

   Uses Github actions secrets and variables. 
   
   In your repo: **Settings → Secrets and variables → Actions**.

- **WEBSITE_URL** – page to fetch
- **WEBSITE_HTML_SELECTOR** – element to read (e.g. `#price`, `.status`, `h1`)
- **WEBSITE_EXPECTED_TEXT** – exact string to compare; if the element’s text differs, an SMS is sent
- **GMAIL_APP_PASSWORD** – App password for the gmail account that will send the emails. Code has a hardcoded email address
- **SMS_RECIPIENTS_AND_CARRIERS** – numbers and carriers email extensions for sending the requests. i the format `1234567890@carrier.com` or .net. The carrier emails used for sending texts differ per carrier.
- **TELEGRAM_BOT_TOKEN** – The telegram bot token for send messages to a telegram bot. Required
- **TELEGRAM_CHAT_ID** – The chat id of the channel to send to. Required

Optional:

- `--log-file PATH` – log file path (default: `check-website.log`)
- `--timeout SECONDS` – page load timeout in seconds (default: 30)

All output is written to the log file and to stdout.

## GitHub Actions (cron schedule)

Workflow runs on a cron schedule and calls the script using values from the repo

