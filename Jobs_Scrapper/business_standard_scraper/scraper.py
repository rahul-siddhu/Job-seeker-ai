import sys
import json
from hashlib import md5
from pytrends.request import TrendReq
from datetime import datetime, timedelta
from fuzzywuzzy import fuzz
from botasaurus.request import Request
from bs4 import BeautifulSoup
import time
import random
from pymongo import MongoClient
from data_dump import MongoDBPipeline  # Import the pipeline from data_dump.py
import os

# MongoDB Connection setup from environment variables
MONGO_URI = os.getenv("MONGO_URI")  # Fetch MongoDB URI from environment variables
MONGO_DATABASE = os.getenv("MONGO_DATABASE")  # Fetch MongoDB database name from environment variables

if not MONGO_URI or not MONGO_DATABASE:
    print("Error: MongoDB URI or database name is not set in environment variables.")
    sys.exit(1)

client = MongoClient(MONGO_URI)
db = client[MONGO_DATABASE]  # Use the database specified in environment variables
collection = db['rawnews']  # Replace with your MongoDB collection name

# Initialize the pipeline
portal_name = 'BusinessStandard'  
pipeline = MongoDBPipeline(db, 'rawnews', portal_name)

# Define headers for requests
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
}

pytrends = TrendReq(hl='en-US', tz=360)

# Retry logic
def retry_request(url, retries=3, delay=2):
    for i in range(retries):
        try:
            response = Request().get(url=url, headers=HEADERS)
            return response.text
        except Exception as e:
            print(f"Error fetching URL {url}: {e}")
            if i < retries - 1:
                sleep_time = delay * (2 ** i) + random.uniform(0, 1)  # Exponential backoff with some randomness
                print(f"Retrying in {sleep_time:.2f} seconds...")
                time.sleep(sleep_time)
    return None

def get_todays_trending_topics():
    trending_topics = {'india': [], 'worldwide': []}
    try:
        india_trending = pytrends.trending_searches(pn='india')
        trending_topics["india"] = india_trending[0].tolist()
        worldwide_trending = pytrends.trending_searches(pn='united_states')
        trending_topics["worldwide"] = worldwide_trending[0].tolist()
        return trending_topics
    except Exception as e:
        print(f"Error fetching trending topics: {e}")
        return trending_topics

def parse_main_page(url, trending_topics):
    print(f"Parsing main page: {url}")
    collected_data = []
    try:
        page_content = retry_request(url)
        if not page_content:
            print(f"Failed to fetch page: {url}")
            return collected_data

        soup = BeautifulSoup(page_content, 'html.parser')
        script_tags = soup.find_all('script', type='application/ld+json')

        item_list_script = None
        for script in script_tags:
            try:
                data = json.loads(script.string)
                if data.get('@type') == 'ItemList':
                    item_list_script = data
                    break
            except json.JSONDecodeError:
                continue

        if item_list_script:
            news_items = item_list_script.get('itemListElement', [])
            for item in news_items:
                detail_url = item.get('url')
                if detail_url:
                    collected_data.extend(parse_detail_page(detail_url, trending_topics))
        else:
            print(f"ItemList not found in script tags on {url}")

        next_page = get_next_page(url)
        if next_page:
            collected_data.extend(parse_main_page(next_page, trending_topics))

    except Exception as e:
        print(f"Error parsing main page {url}: {e}")

    return collected_data

def get_next_page(url):
    if "/page-" in url:
        base_url, current_page = url.rsplit('/', 1)
        page_number = int(current_page.split('-')[-1]) + 1
        return f"{base_url}/page-{page_number}"
    else:
        return f"{url}/page-2"

def is_last_7_days(date_str):
    try:
        article_date = datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S%z').replace(tzinfo=None)
        seven_days_ago = datetime.now() - timedelta(days=7)
        return article_date >= seven_days_ago
    except ValueError as e:
        print(f"Error parsing date '{date_str}': {e}")
        return False

def check_is_trending(title, keywords, trending_topics):
    for topic in trending_topics["india"] + trending_topics["worldwide"]:
        if fuzz.partial_ratio(title.lower(), topic.lower()) > 80 or any(
            fuzz.partial_ratio(keyword.lower(), topic.lower()) > 80 for keyword in keywords.split(",")
        ):
            return True
    return False

def extract_company_name(keywords):
    """Extracts a probable company name from keywords."""
    exclusion_terms = ['service', 'quality', 'social media', 'customer complaints', 'centres', 'issues', 'insurance']
    keywords_list = [kw.strip() for kw in keywords.split(',')]

    for keyword in keywords_list:
        if all(term.lower() not in keyword.lower() for term in exclusion_terms):
            return keyword

    return 'No Company Found'

def parse_detail_page(url, trending_topics):
    print(f"Parsing detail page: {url}")
    collected_data = []
    try:
        page_content = retry_request(url)
        if not page_content:
            print(f"Failed to fetch detail page: {url}")
            return collected_data

        soup = BeautifulSoup(page_content, 'html.parser')
        script_tags = soup.find_all('script', type='application/ld+json')

        news_article = None
        breadcrumb_list = None

        for script in script_tags:
            try:
                data = json.loads(script.string)

                if data.get('@type') == 'NewsArticle':
                    news_article = data

                elif data.get('@type') == 'BreadcrumbList':
                    breadcrumb_list = data
            except json.JSONDecodeError:
                continue

        if news_article:
            publication_date = news_article.get('datePublished', 'No Date Found')
            if not is_last_7_days(publication_date):
                print(f"Article is older than 7 days ({publication_date}). Stopping the script.")
                sys.exit()  # This will stop the script automatically

            title = news_article.get('headline', 'No Title Found')
            keywords = news_article.get('keywords', 'No Keywords')
            company_name = extract_company_name(keywords)
            raw_data = {
                'title': title,
                'description':{
                        'text': news_article.get('description', 'No Description'),
                        'html': news_article.get('description', 'No Description')
                }, 
                'keywords': keywords,
                'company': company_name, 
                'link': url,
                'publicationDate': publication_date,
                'modifiedDate': news_article.get('dateModified', 'No Modified Date Found'),
                'author': [
                    {
                        'name': author.get('name', 'No Name'),
                        'profile_link': author.get('url', 'No Profile Link')
                    }
                    for author in news_article.get('author', [])
                ],
                'source': {
                    'name': news_article.get('publisher', {}).get('name', 'No Publisher'),
                    'logo': news_article.get('publisher', {}).get('logo', {}).get('url', 'No Logo')
                },
                'thumbnailUrl': news_article.get('image', 'No Thumbnail Found'),
                'content':{
                    'text': news_article.get('articleBody', 'No Content Found'),
                    'html': news_article.get('articleBody', 'No Content Found')
                },
                'images': news_article.get('associatedMedia', {}).get('url', []),
                'newsCategory': [
                    item.get('item', {}).get('name', 'No Name')
                    for item in (breadcrumb_list.get('itemListElement', []) if breadcrumb_list else [])
                ],
                'is_trending': check_is_trending(title, keywords, trending_topics),
            }

            raw_data['url_hash'] = md5(url.encode('utf-8')).hexdigest()
            pipeline.process_item({'rawData': raw_data})
            collected_data.append({'rawData': raw_data})

    except Exception as e:
        print(f"Error parsing detail page {url}: {e}")

    return collected_data

def scrape_news(pipeline):
    """
    Function to scrape news and process it using the provided MongoDB pipeline.
    """
    trending_topics = get_todays_trending_topics()
    start_url = 'https://www.business-standard.com/companies/news'
    
    collected_data = parse_main_page(start_url, trending_topics)
    
    # Process each collected item using the pipeline
    for item in collected_data:
        pipeline.process_item(item)  # Process item using the MongoDB pipeline
    
if __name__ == "__main__":
    scrape_news(pipeline)



# ADD
# isDumped: false
# isDeleted: false
# isUpdated: false

# UPDATE
# isDumped: false
# isDeleted: false
# isUpdated: true

# DELETE
# isDumped: false
# isDeleted: true
# isUpdated: false