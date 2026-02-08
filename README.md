# simple-stock-notifier
Runs on a schedule to check a website for an element’s text and sends an SMS (Twilio) when it differs from the expected string.

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set Twilio environment variables (or export them before running):
   - `TWILIO_ACCOUNT_SID` – from Twilio Console
   - `TWILIO_AUTH_TOKEN` – from Twilio Console
   - `TWILIO_FROM_NUMBER` – your Twilio phone number (e.g. `+1234567890`)
   - `TWILIO_TO_NUMBER` – number to receive alerts (e.g. `+1987654321`)

## Usage

```bash
python check-website.py <URL> <CSS_SELECTOR> <EXPECTED_TEXT>
```

- **URL** – page to fetch
- **CSS_SELECTOR** – element to read (e.g. `#price`, `.status`, `h1`)
- **EXPECTED_TEXT** – exact string to compare; if the element’s text differs, an SMS is sent

Examples:

```bash
python check-website.py "https://example.com/product" "#stock-status" "Out of stock"
python check-website.py "https://example.com" "h1" "Welcome"
```

Optional:

- `--log-file PATH` – log file path (default: `check-website.log`)
- `--timeout SECONDS` – HTTP timeout (default: 30)

All output is written to the log file and to stdout.

## GitHub Actions (hourly check)

A workflow runs every hour and calls the script using values from the repo.

1. In your repo: **Settings → Secrets and variables → Actions**.

2. **Secrets** (required for Twilio):
   - `TWILIO_ACCOUNT_SID`
   - `TWILIO_AUTH_TOKEN`
   - `TWILIO_FROM_NUMBER`
   - `TWILIO_TO_NUMBER`

3. **Variables** (required for the check):
   - `CHECK_URL` – URL to fetch (e.g. `https://example.com/product`)
   - `CHECK_SELECTOR` – CSS selector (e.g. `#stock-status`)
   - `CHECK_EXPECTED_TEXT` – expected text (e.g. `Out of stock`)

4. The workflow **Check website** runs on the schedule and can also be triggered manually from the **Actions** tab.
