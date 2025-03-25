import time
import random
import undetected_chromedriver as uc
from urllib.parse import urlparse
import re
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from bs4 import BeautifulSoup
from pymongo import MongoClient
import cloudscraper
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver

# MongoDB Connection
def connect_mongo():
    client = MongoClient("mongodb+srv://lil_boo:lil_boo22@cluster0.qoqzo.mongodb.net/")  
    db = client["blogs"]
    return db["foundr"]

# Extract links using BeautifulSoup
def extract_links(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    return [a["href"] for a in soup.find_all("a", href=True)]

# Set up ChromeDriver with auto-update
import undetected_chromedriver as uc

def setup_driver():
    options = uc.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    
    # Spoof User-Agent to look like a real browser
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

    # Use undetected ChromeDriver to bypass bot detection
    driver = uc.Chrome(options=options, headless=False)
    driver.set_page_load_timeout(30)
    return driver

# Extract blog topic links
def extract_topics(website, class_name, max_retries=3, retry_delay=3):
    parsed_url = urlparse(website)
    domain_name = re.sub(r'^www\\.', '', parsed_url.netloc).split('.')[0]

    driver = setup_driver()
    blogs = []
    retry_count = 0

    while retry_count < max_retries:
        try:
            driver.get(website)
            time.sleep(random.uniform(3, 6))  # Random delay

            WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, class_name)))
            blog_elements = driver.find_elements(By.CLASS_NAME, class_name)
            print(f"Found {len(blog_elements)} elements with class '{class_name}'")
            
            for element in blog_elements[:10]:  # Limit to 10 links
                try:
                    links = extract_links(element.get_attribute("outerHTML"))
                    required_link = links[0] if links else None
                    if required_link:
                        blogs.append({"link": required_link, "domain": domain_name})
                except Exception as e:
                    print(f"Error processing element: {e}")
            break  # Exit loop on success
        except TimeoutException:
            retry_count += 1
            print(f"Timeout on {website}. Retry {retry_count}/{max_retries}")
            time.sleep(retry_delay)
        except Exception as e:
            print(f"Error accessing {website}: {e}")
            break

    driver.quit()

    # Fallback to Cloudscraper if Selenium fails
    if not blogs:
        print("Selenium failed. Trying Cloudscraper...")
        try:
            scraper = cloudscraper.create_scraper()
            response = scraper.get(website)
            if response.status_code == 200:
                blogs = extract_links(response.text)
                blogs = [{"link": link, "domain": domain_name} for link in blogs[:10]]
            else:
                print("Cloudscraper request failed.")
        except Exception as e:
            print(f"Cloudscraper error: {e}")

    return blogs

# Extract blog content
def extract_blog_content(links, class_name, max_retries=3, retry_delay=5):
    if not links:
        print("No links found, skipping content extraction.")
        return

    driver = setup_driver()
    collection = connect_mongo()

    for link_info in links:
        link = link_info['link']
        print(f"Processing: {link}")
        retry_count = 0

        while retry_count < max_retries:
            try:
                driver.get(link)
                time.sleep(random.uniform(3, 6))  # Random delay
                WebDriverWait(driver, 15).until(EC.presence_of_all_elements_located((By.CLASS_NAME, class_name)))

                elements = driver.find_elements(By.CLASS_NAME, class_name)
                if elements:
                    content = elements[0].get_attribute("outerHTML")
                    collection.insert_one({"link": link, "content": content})
                    print(f"Stored content from {link}")
                else:
                    print(f"No elements with class '{class_name}' found on {link}")
                break
            except TimeoutException:
                retry_count += 1
                print(f"Timeout on {link}. Retry {retry_count}/{max_retries}")
                time.sleep(retry_delay)
            except WebDriverException as e:
                print(f"Browser error on {link}: {e}")
                time.sleep(retry_delay * 2)
                retry_count += 1
            except Exception as e:
                print(f"Unexpected error processing {link}: {e}")
                break

    driver.quit()

# List of sites to scrape
sites = [
    {
        "site": "https://foundr.com/articles",
        "class_blog": "entry-content",   # Class name for blog content
        "class_title": "entry-title-link"  # Class name for blog links
    }
]

# Run the script
if __name__ == "__main__":
    for site in sites:
        try:
            links = extract_topics(site['site'], site['class_title'])
            extract_blog_content(links, site['class_blog'])
            print("*" * 50)
        except Exception as e:
            print(f"Error processing site {site['site']}: {e}")
