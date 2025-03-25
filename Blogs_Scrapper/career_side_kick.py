import json
from selenium import webdriver
from urllib.parse import urlparse
import re
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def extract_links(text):
    url_pattern = r"https?://[^\s<>\"']+"  # Matches http or https URLs
    return re.findall(url_pattern, text)

from bs4 import BeautifulSoup

def extract_links(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    links = [a["href"] for a in soup.find_all("a", href=True)]
    return links

def extract_topics(website, class_name):
    # Extract domain name from website URL
    parsed_url = urlparse(website)
    domain_name = re.sub(r'^www\.', '', parsed_url.netloc).split('.')[0]  # Remove 'www.' and get main domain

    # Set up Selenium WebDriver
    options = webdriver.ChromeOptions()
    # options.add_argument("--headless")  # Remove for debugging
    driver = webdriver.Chrome(options=options)
    driver.get(website)  

    # Wait for elements to be present
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, class_name)))
    except Exception as e:
        print(f"Error: Unable to find elements with class {class_name}. Check if the website structure has changed.")
        driver.quit()
        return []

    # Find all blog post elements
    blog_elements = driver.find_elements(By.CLASS_NAME, class_name)

    print(f"Found {len(blog_elements)} elements with class '{class_name}'")

    blogs = []
    limit=10
    for element in blog_elements:
        if(limit==0):
            break
        limit-=1
        links = extract_links(element.get_attribute("outerHTML"))
        if links:
            blogs.append({"link": links[0]})

    driver.quit()

    if not blogs:
        print("No blog links found. Check the class name or website structure.")

    file_name = f"{domain_name}_links.json"

    with open(file_name, "w") as file:
        json.dump(blogs, file, indent=4)

    print(f"Blog data saved to {file_name}")
    return blogs

def extract_blog_content(website, links, class_name):
    if not links:
        print("No links found, skipping content extraction.")
        return {}

    parsed_url = urlparse(website)
    domain_name = re.sub(r'^www\.', '', parsed_url.netloc).split('.')[0]

    options = webdriver.ChromeOptions()
    # options.add_argument("--headless")  # Remove for debugging
    driver = webdriver.Chrome(options=options)
    data_list = {}

    for link in links:
        driver.get(link['link'])
        try:
            WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, class_name)))
        except Exception as e:
            print(f"Error: Unable to find elements on {link['link']}")
            continue

        elements = driver.find_elements(By.CLASS_NAME, class_name)

        if elements:
            data_list[link['link']] = elements[0].get_attribute("outerHTML")

    driver.quit()

    file_name = f"{domain_name}.json"
    with open(file_name, "w") as file:
        json.dump(data_list, file, indent=4)

    print(f"Blog content saved to {file_name}")
    return data_list

if __name__ == "__main__":
    sites = [
        {
            "site":"https://careersidekick.com/",
            "class_blog":"inside-article",
            "class_title":"h3.gb-headline-text a"
        }
        {
            "site":"https://feedly.com/i/subscription/feed%2Fhttp%3A%2F%2Flongreads.com%2Frss",
            "class_blog":"site-content",
            "class_title":"y1fnj_DjEQF3FRtK8Tf1"
        },
        {
            "site":"https://dev.to/",
            "class_blog":"crayons-article__main ",
            "class_title":"crayons-story__title"
        }
    ]

    for site in sites:
        links = extract_topics(site['site'], site['class_title'])
        extract_blog_content(site['site'], links, site['class_blog'])
        print("*" * 50)
