"""This script navigates to Etsy's investor relations page, clicks on 'Our Leadership',
and extracts the names and titles of Etsy's leadership team."""

import agentql
from playwright.sync_api import sync_playwright
import requests


# Set the URL to Etsy's main page
URL = "https://www.etsy.com"

# Define the queries to interact with the page
MAIN_PAGE_QUERY = """
{
    investors_link
}
"""

INVESTORS_PAGE_QUERY = """
{
    our_leadership_link
}
"""

LEADERSHIP_PAGE_QUERY = """
{
    leadership_team[] {
        name
        title
    }
}
"""

def start_browser(p):
    """Starts the browser and returns the browser instance"""
    ws_response = requests.get("http://127.0.0.1:9222/json/version")
    WEBSOCKET_URL = ws_response.json()["webSocketDebuggerUrl"]
    print(f"Connecting to WebSocket URL: {WEBSOCKET_URL}")
    # Connect to the browser via Chrome DevTools Protocol
    browser =  p.chromium.connect_over_cdp(WEBSOCKET_URL)

    return browser

def main():
    with sync_playwright() as playwright:
        browser = start_browser(playwright)
        page = agentql.wrap(browser.new_page())

        # Navigate to Etsy's main page
        page.goto(URL)

        # Find and click the Investors link
        response = page.query_elements(MAIN_PAGE_QUERY)
        response.investors_link.click()

        # Find and click the Our Leadership link
        response = page.query_elements(INVESTORS_PAGE_QUERY)
        response.our_leadership_link.click()

        # Extract leadership team information
        response = page.query_data(LEADERSHIP_PAGE_QUERY)

        # Print the extracted data
        print("Etsy Leadership Team:")
        for leader in response.leadership_team:
            print(f"Name: {leader.name}, Title: {leader.title}")

        # Close the browser
        browser.close()

if __name__ == "__main__":
    main()