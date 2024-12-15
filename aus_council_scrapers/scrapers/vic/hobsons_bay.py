from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

from aus_council_scrapers.base import BaseScraper, ScraperReturn, register_scraper
from bs4 import BeautifulSoup
import re


@register_scraper
class HobsonsBayScraper(BaseScraper):
    def __init__(self):
        council = "hobsons_bay"
        state = "VIC"
        base_url = "https://www.hobsonsbay.vic.gov.au/"
        self.webpage_url = "https://www.hobsonsbay.vic.gov.au/Council/Council-Meetings/Minutes-and-Agendas"
        super().__init__(council, state, base_url)
        self.time_pattern = re.compile(r"\d+:\d+\s?[apmAPM]+")

    def scraper(self) -> ScraperReturn | None:

        # Initialise driver

        chrome_options = Options()
        chrome_options.add_argument("--headless")
        driver = webdriver.Chrome(options=chrome_options)

        # Assign initial values to variables that will be returned 

        name = None
        date = None
        meeting_time = None
        download_url = None

        # Retrieve webpage

        driver.get(self.webpage_url)
        driver.refresh()

        # Open accordions 

        elements = driver.find_elements(By.XPATH, "//a[contains(@class, 'accordion-trigger')]")
        for element in elements:
            driver.execute_script("arguments[0].click();", element)

        wait = WebDriverWait(driver, 15)
        wait.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, ".accordion-list-item-container .initialised")
            )
        )

        output = driver.page_source
        driver.quit()

        soup = BeautifulSoup(output, "html.parser")

        meetings = soup.find_all("div", class_="accordion-list-item-container")

        for meeting in meetings:
            document_link = meeting.find("a", class_="document")
            if not document_link:
                continue
            
            name = meeting.find("h2", class_="item-text").text
            print(name)
            date = meeting.find("span", class_="minutes-date").text
            time = meeting.find("div", class_="meeting-time").text
            print(time)

            if time:
                time_match = self.time_pattern.search(time)
                meeting_time = time_match.group()
                print(meeting_time)
            
            download_url = self.base_url + document_link["href"]
            print(download_url)
            break

        return ScraperReturn(
            name = name,
            date = date,
            time = meeting_time,
            webpage_url = self.webpage_url,
            download_url = download_url
        )

if __name__ == "__main__":
    scraper = HobsonsBayScraper()
    scraper.scraper()
