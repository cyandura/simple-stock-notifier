#!/usr/bin/env python3
"""
Check a URL for an element's text. If it differs from the expected string,
send an SMS. All output is logged to a file.

Uses a headless browser (Playwright) so the site sees real JavaScript and cookies,
avoiding "enable JavaScript and cookies" blocks that curl/requests get.
"""

import argparse
import logging
import sys
import send_email
import send_telegram
from pathlib import Path

from playwright.sync_api import sync_playwright


# Default log file path (same directory as script)
SCRIPT_DIR = Path(__file__).resolve().parent
LOG_FILE = SCRIPT_DIR / "check-website.log"

log = logging.getLogger()

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


def parse_recipients(value: str) -> list[str]:
    """
    Parse a string of "number:gateway" pairs into a list of (number, gateway) tuples.
    Example: "1124512662:tmomail.net,15551234567:vtext.com" -> [("1124512662", "tmomail.net"), ...]
    """
    if not value or not value.strip():
        return []
    result = []
    for part in value.split(","):
        part = part.strip()
        result.append(part)
    return result


def get_element_text_with_browser(url: str, selector: str, timeout: float = 30000) -> str | None:
    """
    Open the URL in a headless Chromium browser (JavaScript and cookies enabled),
    wait for load, then return the text of the first element matching the CSS selector.
    Returns None if the element is not found.
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1280, "height": 720},
            locale="en-US",
        )
        page = context.new_page()
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=timeout)
            # Give JS a moment to run (e.g. dynamic content)
            page.wait_for_timeout(2000)
            locator = page.locator(selector)
            if locator.count() == 0:
                return None
            text = locator.first.text_content(timeout=5000)
            return text.strip() if text else None
        finally:
            browser.close()
    return None


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check a URL for element text; send SMS if it differs."
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
        "email_app_password",
        help="App Password for the email that is sending the notification.",
    )
    parser.add_argument(
        "to_numbers",
        help='Recipients as "number:gateway" pairs, comma-separated (e.g. 1124512662:tmomail.net,15551234567:vtext.com)',
    )
    parser.add_argument(
        "telegram_bot_token",
        help='Telegram bot token',
    )
    parser.add_argument(
        "telegram_chat_id",
        help='Telegram chat ID',
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
        help="Page load timeout in seconds (default: 30)",
    )
    args = parser.parse_args()

    setup_logging(args.log_file)

    log.info("Checking URL with selector: %s)", args.selector)

    try:
        found_text = get_element_text_with_browser(
            args.url,
            args.selector,
            timeout=args.timeout * 1000,
        )
    except Exception as e:
        log.exception("Failed to load page: %s", e)
        return 1

    if found_text is None:
        log.warning("No element found for selector: %s", args.selector)
        found_text = "text_not_found, check HTML selector"

    if found_text == args.expected:
        log.info("Text matches expected: %r", args.expected)
        return 0

    recipients = parse_recipients(args.to_numbers)

    message = f'The webpage has changed! Expected: {args.expected} | Found: {found_text}'
    for number_carrier_hostname in recipients:
        send_email.send_email(args.email_app_password, number_carrier_hostname, message)

    send_telegram.send_telegram(args.telegram_bot_token, args.telegram_chat_id, message)

    log.info(message)

    return 0


if __name__ == "__main__":
    sys.exit(main())
