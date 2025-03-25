# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class FreshersworldJobItem(scrapy.Item):
    title = scrapy.Field()
    rating = scrapy.Field()
    reviewsCount = scrapy.Field()
    salary = scrapy.Field()
    location = scrapy.Field()
    postedAt = scrapy.Field()
    description = scrapy.Field()
    applyUrls = scrapy.Field()
    jobType = scrapy.Field()
    experience = scrapy.Field()
    postedBy = scrapy.Field()
    openings = scrapy.Field()
    applicants = scrapy.Field()
    qualification = scrapy.Field()
    isBlackListed = scrapy.Field()
    isExpired = scrapy.Field()
    job_function = scrapy.Field()
    mainStream = scrapy.Field()
    hiringProcess =  scrapy.Field()
    
    pass
