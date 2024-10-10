"""This script navigates to Etsy's investor relations page, clicks on 'Our Leadership',
and extracts the names and titles of Etsy's leadership team."""

import agentql
from playwright.async_api import BrowserContext, async_playwright
import requests
import csv
import asyncio
import json

# Run on exisiting browser to prevent popups. First run the below code, then replace websocket url with what is given 
# /Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222
WEBSOCKET_URL = "ws://127.0.0.1:9222/devtools/browser/67b5734f-aadd-4c16-8ab2-0fbfd2d576f9"

# Define the queries to interact with the page

POPUP_QUERY = """
{
    popup_form {
        close_btn
    }
}
"""

async def get_described_query(described_query):
    return f"""{{
    link(get link for{described_query}, do not click product listings or advertisements)
}}""".strip()


GOOGLE_URL = "https://www.google.com/"

async def search(page, company, query):

    GOOGLE_SEARCH_QUERY = """
    {
        search_input
        search_btn
    }
    """

    await page.goto(GOOGLE_URL)

    search_elements = await page.query_elements(GOOGLE_SEARCH_QUERY)
    search = f"{company} {query}"
    await search_elements.search_input.fill(search)
    await search_elements.search_btn.click()
    print(search)
    await page.keyboard.press("Enter")
    await page.wait_for_page_ready_state()
    described_query = await get_described_query(f"{company} {query}")
    print(described_query)
    link_response = await page.query_elements(described_query)
    await link_response.link.click()
    await page.wait_for_page_ready_state()

async def get_leaders(page, company):

    await search(page, company, "executive leadership team")

    await page.wait_for_timeout(5000)

    LEADERSHIP_PAGE_QUERY = """
    {
        leadership_team[] {
            name    
            title
        }
    }
    """

    popup_response = await page.query_elements(POPUP_QUERY)
    if popup_response.popup_form.close_btn is not None:
        await popup_response.popup_form.close_btn.click()
    response = await page.query_data(LEADERSHIP_PAGE_QUERY)
    results = response['leadership_team']
    print(results)
    return results


async def get_globaldata(page, company):

    await search(page, company, "globaldata")

    GET_GLOBALDATA_QUERY = """
    {
        company_info
        {
            company_name
            industry
            employee_count
            revenue
        }
        products_and_services[]
        {
            value
        }
    }
    """

    response = await page.query_data(GET_GLOBALDATA_QUERY)
    output = []
    company_info = response['company_info']
    print(company_info)

    return company_info

# Define the queries to interact with the page

async def extract_articles(page, company):

    await search(page, company, "yahoo news")

    NEWS_QUERY = """
    {
        news_articles[] {
            title
            link
        }
    }
    """

    popup_response = await page.query_elements(POPUP_QUERY)
    print(popup_response)

    if popup_response.popup_form.close_btn is not None:
        await popup_response.popup_form.close_btn.click()
    response = await page.query_data(NEWS_QUERY)
    results = response['news_articles']
    return results

async def extract_sec_filings(page, company):

    SEC_WEBSITE = "https://www.sec.gov/edgar/search"

    SEARCH_BUTTON = """
    {
        search_input
    }
    """

    GET_QUARTERLY_REPORT = """
    {
        quarterly_report_10q(grab the lates available one)
    }
    """

    OPEN_DOCUMENT = """
    {
        open_document_url
    }
    """

    SEC_QUERY = """
    {
        summary_of_risk_factors[]
    }
    """


    await page.goto(SEC_WEBSITE)
    await page.wait_for_page_ready_state()
    search_box = await page.query_elements(SEARCH_BUTTON)
    await search_box.search_input.fill(company)
    await page.keyboard.press("Enter")
    await page.wait_for_page_ready_state()

    report_link = await page.query_elements(GET_QUARTERLY_REPORT)
    await report_link.quarterly_report_10q.click()

    open_document = await page.query_data(OPEN_DOCUMENT)
    await page.goto(open_document['open_document_url'])
    await page.wait_for_page_ready_state()

    risk_factors_response = await page.query_data(SEC_QUERY)
    risk_factors = risk_factors_response['summary_of_risk_factors']

    print(risk_factors)

    return risk_factors


async def extract_all(browser, company):
    context = await browser.new_context()
    page = await agentql.wrap(context.new_page())

    globaldata = await get_globaldata(page, company)
    leaders = await get_leaders(page, company)
    articles = await extract_articles(page, company)
    risk_factors = await extract_sec_filings(page, company)

    return {
        f"company": {
            "GLOBAL DATA INFORMATION": globaldata,
            "EXECUTIVE LEADERSHIP TEAM": leaders,
            "LATEST NEWS": articles,
            "SUMMARY RISK FACTORS": risk_factors
        }
    }


async def extract_intelligence(companies):

    async with async_playwright() as playwright:

        browser = await playwright.chromium.launch(headless=False)
        tasks = [extract_all(browser, company) for company in companies]
        results = await asyncio.gather(*tasks)
        print(results)

    with open("results.txt", "w") as file:
        file.write(str(results))


if __name__ == "__main__":
    companies = ["Etsy", "Williams Sonoma", "Blue apron", "Wayfair", "Honest Company "]
    asyncio.run(extract_intelligence(companies))
        
