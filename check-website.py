#!/usr/bin/env python3
"""
Check a URL for an element's text. If it differs from the expected string,
send an SMS via Twilio. All output is logged to a file.
"""

import argparse
import logging
import os
import sys
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from twilio.rest import Client


# Default log file path (same directory as script)
SCRIPT_DIR = Path(__file__).resolve().parent
LOG_FILE = SCRIPT_DIR / "check-website.log"


def setup_logging(log_path: Path) -> None:
    """Configure logging to file and optionally to console."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.FileHandler(log_path, encoding="utf-8"),
            logging.StreamHandler(sys.stdout),
        ],
    )


def fetch_page(url: str, timeout: int = 30) -> str:
    """Fetch the page HTML. Raises on failure."""
    resp = requests.get(url, timeout=timeout)
    resp.raise_for_status()
    return resp.text


def get_element_text(html: str, selector: str) -> str | None:
    """Parse HTML and return the text of the first element matching the CSS selector."""
    soup = BeautifulSoup(html, "html.parser")
    el = soup.select_one(selector)
    if el is None:
        return None
    return el.get_text(strip=True)


def send_twilio_sms(
    body: str,
    account_sid: str,
    auth_token: str,
    from_number: str,
    to_number: str,
) -> bool:
    """Send an SMS via Twilio. Returns True on success."""
    client = Client(account_sid, auth_token)
    client.messages.create(body=body, from_=from_number, to=to_number)
    return True


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check a URL for element text; send Twilio SMS if it differs."
    )
    parser.add_argument("url", help="URL to fetch")
    parser.add_argument(
        "selector",
        help="CSS selector for the element (e.g. '#price', '.status', 'h1')",
    )
    parser.add_argument(
        "expected",
        help="Expected text (exact match). If element text differs, SMS is sent.",
    )
    parser.add_argument(
        "--log-file",
        type=Path,
        default=LOG_FILE,
        help=f"Log file path (default: {LOG_FILE})",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=30,
        help="HTTP request timeout in seconds (default: 30)",
    )
    args = parser.parse_args()

    setup_logging(args.log_file)
    log = logging.getLogger()

    # Twilio credentials from environment
    account_sid = os.environ.get("TWILIO_ACCOUNT_SID")
    auth_token = os.environ.get("TWILIO_AUTH_TOKEN")
    from_number = os.environ.get("TWILIO_FROM_NUMBER")
    to_number = os.environ.get("TWILIO_TO_NUMBER")

    if not all([account_sid, auth_token, from_number, to_number]):
        log.error(
            "Missing Twilio env vars: TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, "
            "TWILIO_FROM_NUMBER, TWILIO_TO_NUMBER"
        )
        return 1

    log.info("Checking URL: %s (selector: %s)", args.url, args.selector)

    try:
        html = fetch_page(args.url, timeout=args.timeout)
    except requests.RequestException as e:
        log.exception("Failed to fetch URL: %s", e)
        return 1

    found_text = get_element_text(html, args.selector)
    if found_text is None:
        log.warning("No element found for selector: %s", args.selector)
        # Treat "element not found" as a change and notify
        found_text = ""

    if found_text == args.expected:
        log.info("Text matches expected: %r", args.expected)
        return 0

    log.info("Text differs. Expected: %r | Found: %r", args.expected, found_text)
    message = (
        f"Website check alert: text changed.\n"
        f"URL: {args.url}\n"
        f"Expected: {args.expected}\n"
        f"Found: {found_text}"
    )

    try:
        send_twilio_sms(
            body=message,
            account_sid=account_sid,
            auth_token=auth_token,
            from_number=from_number,
            to_number=to_number,
        )
        log.info("SMS sent successfully to %s", to_number)
    except Exception as e:
        log.exception("Failed to send SMS: %s", e)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
