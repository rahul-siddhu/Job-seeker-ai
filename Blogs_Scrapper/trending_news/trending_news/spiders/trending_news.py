import scrapy
import json
from pytrends.request import TrendReq
from urllib.parse import urlencode

# mZ3RIc --> class for topic name
class GoogleTrendsSpider(scrapy.Spider):
    name = "google_trends"

    def start_requests(self):
        self.pytrends = TrendReq()

        try:
            print("hiiiiiiii")
            trending_searches = self.pytrends.trending_searches()
            print("hiiiiiiii")
            topics = trending_searches[0].tolist()  # Extract trending topics

            if not topics:
                self.logger.error("No trending topics found.")
                return

            # Save topics to JSON file
            with open("trending_topics.json", "w", encoding="utf-8") as f:
                json.dump(topics, f, ensure_ascii=False, indent=4)

            # Yield topics as Scrapy items
            for topic in topics:
                yield {"topic": topic}

        except Exception as e:
            self.logger.error(f"Failed to fetch trending searches: {e}")

class GoogleNewsSpider(scrapy.Spider):
    name = "google_news"
    allowed_domains = ["news.google.com"]

    def start_requests(self):
        with open("trending_topics.json", "r") as f:
            topics = json.load(f)

        for topic in topics:
            params = {"q": topic, "hl": "en", "gl": "US", "ceid": "US:en"}
            url = f"https://news.google.com/rss/search?{urlencode(params)}"
            yield scrapy.Request(url, callback=self.parse, meta={"topic": topic})

    def parse(self, response):
        topic = response.meta["topic"]
        for item in response.xpath("//item"):
            yield {
                "topic": topic,
                "title": item.xpath("title/text()").get(),
                "link": item.xpath("link/text()").get(),
                "source": item.xpath("source/text()").get(),
                "published": item.xpath("pubDate/text()").get(),
            }
