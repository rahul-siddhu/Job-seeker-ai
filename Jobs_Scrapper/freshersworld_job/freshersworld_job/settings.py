# Scrapy settings for freshersworld_job project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = "freshersworld_job"

SPIDER_MODULES = ["freshersworld_job.spiders"]
NEWSPIDER_MODULE = "freshersworld_job.spiders"

# Obey robots.txt rules
ROBOTSTXT_OBEY = True

# Configure maximum concurrent requests performed by Scrapy (default: 16)
CONCURRENT_REQUESTS = 32  # Increased to speed up crawling

# Configure a delay for requests for the same website (default: 0)
DOWNLOAD_DELAY = 0.5  # 1-second delay between requests for the same domain
CONCURRENT_REQUESTS_PER_DOMAIN = 16 
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
COOKIES_ENABLED = True


# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
#    "Accept-Language": "en",
#}

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    "freshersworld_job.middlewares.FreshersworldJobSpiderMiddleware": 543,
#}

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#DOWNLOADER_MIDDLEWARES = {
#    "freshersworld_job.middlewares.FreshersworldJobDownloaderMiddleware": 543,
#}

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    "scrapy.extensions.telnet.TelnetConsole": None,
#}

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
   "freshersworld_job.pipelines.MongoPipeline": 300,
}

# LOG_ENABLED = True
# LOG_LEVEL = 'INFO'

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 0.5
AUTOTHROTTLE_MAX_DELAY = 2
AUTOTHROTTLE_TARGET_CONCURRENCY = 3.0

# Enable HTTP caching to reduce unnecessary load on the server (optional)
HTTPCACHE_ENABLED = True
HTTPCACHE_EXPIRATION_SECS = 3600  # Cache items for an hour
HTTPCACHE_DIR = "httpcache"
HTTPCACHE_IGNORE_HTTP_CODES = [500, 502, 503, 504, 408]  # Ignore caching for server-side errors
HTTPCACHE_STORAGE = "scrapy.extensions.httpcache.FilesystemCacheStorage"

# Set settings whose default value is deprecated to a future-proof value
REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"

# Retry failed requests
RETRY_ENABLED = True
RETRY_TIMES = 2

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# MongoDB credentials
MONGO_URI = os.getenv("MONGO_URI")
MONGO_DATABASE = os.getenv("MONGO_DATABASE")

# STATS_DUMP = True 

BATCH_SIZE = 200