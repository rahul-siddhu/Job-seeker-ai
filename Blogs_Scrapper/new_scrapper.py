from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import pandas as pd
from datetime import datetime

class GoogleTrendsNewsScraper:
    def __init__(self):
        self.setup_driver()
        self.trending_topics = []
        self.news_data = []
        
    def setup_driver(self):
        # Set up Chrome options
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run in headless mode, comment this out to see the browser
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        # Set up the Chrome driver
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=chrome_options
        )
        
    def extract_trending_topics(self):
        try:
            # Navigate to Google Trends
            self.driver.get("https://trends.google.com/trending?geo=IN&hl=en-US&category=3")
            print("Waiting for Google Trends page to load...")
            
            # Wait for the trending topics to load (the div class "mZ3RIc" contains topic titles)
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "mZ3RIc"))
            )
            
            # Extract the trending topics
            trending_elements = self.driver.find_elements(By.CLASS_NAME, "mZ3RIc")
            
            print(f"Found {len(trending_elements)} trending topics")
            
            # Store the trending topics
            for element in trending_elements[:10]:  # Limit to top 10 for demonstration
                topic = element.text.strip()
                if topic:
                    self.trending_topics.append(topic)
                    
            print(f"Extracted topics: {self.trending_topics}")
            return self.trending_topics
            
        except Exception as e:
            print(f"Error extracting trending topics: {e}")
            return []
            
## news url- https://news.google.com/search?for={topic[0]}+{topic[1]}&hl=en-IN&gl=IN&ceid=IN%3Aen
    def scrape_news_for_topics(self):
        if not self.trending_topics:
            print("No trending topics to search for news")
            return []
            
        for topic in self.trending_topics:
            try:
                param=[]
                cur=""
                for x in topic:
                    if x==" ":
                        param.append(cur)
                        cur=""
                    else:
                        cur+=x
                # Construct the Google News search URL
                for i in range(len(param)):
                    if i==0:
                        search_url = f"https://news.google.com/search?for={param[i]}"
                    else:
                        search_url += f"+{param[i]}"
                search_url += "&hl=en-IN&gl=IN&ceid=IN%3Aen"
                
                print(f"Searching news for: {topic}")
                self.driver.get(search_url)
                
                # Wait for news articles to load
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_all_elements_located((By.TAG_NAME, "article"))
                )
                
                # Extract news articles
                articles = self.driver.find_elements(By.TAG_NAME, "article")[:5]  # Limit to 5 articles per topic
                
                for article in articles:
                    try:
                        # Extract article title
                        title_element = article.find_element(By.TAG_NAME, "h3")
                        title = title_element.text.strip()
                        
                        # Extract article link
                        link_element = article.find_element(By.TAG_NAME, "a")
                        link = link_element.get_attribute("href")
                        
                        # Extract publisher
                        publisher_element = article.find_element(By.TAG_NAME, "time").find_element(By.XPATH, "./preceding-sibling::div")
                        publisher = publisher_element.text.strip()
                        
                        # Extract publish time
                        time_element = article.find_element(By.TAG_NAME, "time")
                        publish_time = time_element.text.strip()
                        
                        # Store the news data
                        self.news_data.append({
                            "topic": topic,
                            "title": title,
                            "publisher": publisher,
                            "publish_time": publish_time,
                            "link": link
                        })
                        
                    except Exception as e:
                        print(f"Error extracting article data: {e}")
                        continue
                        
                print(f"Extracted {len(articles)} news articles for '{topic}'")
                
            except Exception as e:
                print(f"Error scraping news for topic '{topic}': {e}")
                continue
                
        return self.news_data
        
    def save_to_csv(self, filename=None):
        if not self.news_data:
            print("No news data to save")
            return
            
        if not filename:
            current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"trending_news_{current_time}.csv"
            
        df = pd.DataFrame(self.news_data)
        df.to_csv(filename, index=False)
        print(f"Data saved to {filename}")
        
    def close(self):
        self.driver.quit()
        
def main():
    scraper = GoogleTrendsNewsScraper()
    
    try:
        # Step 1: Extract trending topics
        trending_topics = scraper.extract_trending_topics()
        print("************")
        print(trending_topics)
        print("************")
        if trending_topics:
            # Step 2: Scrape news for each topic
            news_data = scraper.scrape_news_for_topics()
            
            # Step 3: Save the data
            scraper.save_to_csv()
            
    except Exception as e:
        print(f"An error occurred: {e}")
        
    finally:
        scraper.close()
        
if __name__ == "__main__":
    main()