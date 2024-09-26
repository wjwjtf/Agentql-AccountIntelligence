"""This script navigates to GlobalData's Etsy Inc. company profile and extracts basic company information."""

import os
import csv
import agentql
from playwright.sync_api import sync_playwright

# Set the URL to the desired website
URL = "https://www.globaldata.com/company-profile/etsy-inc/"

# Define the queries to interact with the page
QUERY = """
{
    company_info
    {
        industry
        employee_count
        website
        revenue
    }
    products_and_services[]
    {
        name(Give only meaningful names)
    }
}
"""

def main():
    with sync_playwright() as playwright, playwright.chromium.launch(headless=False) as browser:
        
        # Create a new page in the browser and wrap it to get access to the AgentQL's querying API
        page = agentql.wrap(browser.new_page())

        page.goto(URL)

        # Use query_data() method to fetch the data from the page
        response = page.query_data(QUERY)

        print(f"Data  {response}")

if __name__ == "__main__":
    main()