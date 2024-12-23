import requests
from bs4 import BeautifulSoup
import logging
import time
from requests.exceptions import RequestException

logger = logging.getLogger(__name__)

# Scarpes course data from a given url based on search terms.
def scrape_course_data(url, search_terms):
    max_retries = 3
    retry_delay = 5
    courses = []
    for attempt in range(max_retries):
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
            }
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, "html.parser")
            for course_element in soup.find_all("div", class_="course"):
                title = course_element.find("h2").text.strip()
                if any(term.lower() in title.lower() for term in search_terms):
                    description = course_element.find("p").text.strip()
                    link = course_element.find("a")["href"]

                    courses.append({
                        "title": title,
                        "description": description,
                        "link": link,
                    })
                time.sleep(1)
            return courses
        except RequestException as e:
            logger.error(f"Attempt {attempt + 1} failed: Error during web scraping: {e}")
            if attempt < max_retries - 1:
                logger.info(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                logger.error(f"Failed to scrape data after {max_retries} attempts.")
                return None
        except Exception as e:
            logger.error(f"An unexpected error occurred during scraping: {e}")
            return None