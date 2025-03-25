import scrapy
import json
from datetime import datetime
from bs4 import BeautifulSoup


class JobsSpider(scrapy.Spider):
    name = 'details'
    allowed_domains = ['freshersworld.com']
    start_urls = ['https://www.freshersworld.com/jobs']
    
    # Enum mappings
    Currencies = {
        'INR': 'INR'
    }

    Frequencies = {
        'hourly': 'hourly',
        'daily': 'daily',
        'month': 'monthly',
        'p.a': 'annually',
        'Year': 'annually'
    }

    JobTypes = {
        'FULL_TIME': 'Full time',
        'PART_TIME': 'Part time',
        'INTERNSHIP_/_PROJECTS': 'Internship',
        'Freelance': 'Freelance'
    }

    WorkModels = {
        'In Office': 'InOffice',
        'From Home': 'FromHome',
        'Hybrid': 'Hybrid'
    }

    ExperienceLevels = {
        'Intern Level': 'InternLevel',
        'Entry Level': 'EntryLevel',
        'Mid Level': 'MidLevel',
        'Senior Level': 'SeniorLevel',
        'Director': 'Director',
        'Executive': 'Executive'
    }

    def parse(self, response):
        categories = response.css('div.categories-filter')
        for category in categories:
            page_url = response.urljoin(category.css('::attr(data-page_url)').get())
            category_name = category.css('input.category_id::attr(value)').get()
            yield scrapy.Request(page_url, callback=self.parse_category, meta={'category_name': category_name})

    def parse_category(self, response):
        category_name = response.meta['category_name']
        job_urls = response.css('script[type="application/ld+json"]::text').get()
        if job_urls:
            job_data = json.loads(job_urls)
            for job in job_data.get('itemListElement', []):
                job_url = job.get('url')
                if job_url:
                    yield scrapy.Request(job_url, callback=self.parse_job, meta={'category_name': category_name, 'job_url': job_url})

        total_jobs = response.css('div.jos_count span.number-of-jobs::text').get()
        total_jobs = int(total_jobs) if total_jobs else 0
        limit = 20
        offset = response.meta.get('offset', 0)

        if offset + limit < total_jobs:
            next_page = f"{response.url}?&limit={limit}&offset={offset + limit}"
            yield scrapy.Request(next_page, callback=self.parse_category, meta={'category_name': category_name, 'offset': offset + limit})

    def parse_job(self, response):
        category_name = response.meta['category_name']
        json_ld = response.xpath('//script[@type="application/ld+json"]/text()').get()
        job_details = {}

        if json_ld:
            job_data = json.loads(json_ld)

            raw_description = job_data.get('description', '')
            clean_description = self.remove_html_tags(raw_description)

            job_location = job_data.get('jobLocation', [])

            # If jobLocation is a list, ensure it has items before trying to access it
            if isinstance(job_location, list) and len(job_location) > 0:
                job_location = job_location[0]

            # If jobLocation is still a dictionary, extract the address details
            if isinstance(job_location, dict):
                area = job_location.get('address', {}).get('streetAddress', '')
                if area == 'NA':
                    area = ''  # Replace 'NA' with an empty string

                country = job_location.get('address', {}).get('addressCountry', '')
                if country == 'IN':
                    country = 'India'  # Replace 'IN' with 'India'

                city = job_location.get('address', {}).get('addressLocality', '')
                state = job_location.get('address', {}).get('addressRegion', '')
            else:
                # In case the location is not structured as expected, you can handle the error case
                area = city = state = country = ''

            # Mapping job details to the desired structure
            job_details = {
                "id": job_data.get('identifier', {}).get('value', ''),
                "designation": job_data.get('title', ''),
                "company": job_data.get('identifier', {}).get('name', ''),
                "industry": job_data.get('industry', ''),
                "jobFunction": '',  # Set based on your logic if applicable
                "skills": [],  # Populate skills if available
                "salary": {
                    "min": {
                        "amount": job_data.get('baseSalary', {}).get('value', {}).get('minValue', ''),
                        "currency": self.Currencies.get(job_data.get('baseSalary', {}).get('currency', ''), '')
                    },
                    "max": {
                        "amount": job_data.get('baseSalary', {}).get('value', {}).get('maxValue', ''),
                        "currency": self.Currencies.get(job_data.get('baseSalary', {}).get('currency', ''), '')
                    },
                    "frequency": self.Frequencies.get(job_data.get('baseSalary', {}).get('value', {}).get('unitText', '').lower(), ''),
                    "description": ''
                },
                "location": {
                    "area": area,  # Updated area field
                    "city": city,
                    "state": state,
                    "country": country  # Updated country field
                },
                "postedAt": job_data.get('datePosted', ''),
                "scrapedAt": self.format_datetime(datetime.utcnow()),
                "applyUrls": {
                    "jobUrl": response.url,
                    "externalUrl": ''
                },
                "jobType": self.JobTypes.get(job_data.get('employmentType', '').strip(), ''),
                "workModel": '',
                "experience": {
                    "range": {
                        "from": job_data.get('experienceRequirements', {}).get('minExperience', 0),
                        "to": job_data.get('experienceRequirements', {}).get('maxExperience', 0)
                    },
                    "level": self.ExperienceLevels.get(job_data.get('experienceRequirements', {}).get('level', ''), '')
                },
                "postedBy": {
                    "url": job_data.get('hiringOrganization', {}).get('url', ''),
                    "name": job_data.get('hiringOrganization', {}).get('name', '')
                },
                "applicants": '',  # Populate if available
                "about": {
                    "text": self.remove_html_tags(job_data.get('about', '')),
                    "html": job_data.get('about', '')
                },
                "jobDetail": {
                    "text": clean_description,
                    "html": raw_description
                },
                "qualification": {
                    "text": job_data.get('qualifications', ''),
                    "html": job_data.get('qualifications', '')
                },
                "isBlackListed": False,
                "isExpired": False
            }


            job_details = self.replace_na_with_empty(job_details)

            data_to_insert = {
                'portal': 'Freshersworld',
                'jobPostedAt': job_data.get('datePosted', ''),
                'isDumped': False,
                'rawData': job_details,
            }

            yield data_to_insert

    def remove_html_tags(self, text):
        """Remove HTML tags from text."""
        soup = BeautifulSoup(text, "html.parser")
        return soup.get_text(strip=True)

    def format_datetime(self, date_str):
        """Format the date string to ISO format."""
        if isinstance(date_str, datetime):
            return date_str.isoformat()
        try:
            return datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S').isoformat()
        except ValueError:
            self.logger.error(f"Error parsing date: {date_str}")
            return None

    def replace_na_with_empty(self, data):
        """Recursively replace 'NA' with an empty string in a dictionary or list."""
        if isinstance(data, dict):
            return {key: self.replace_na_with_empty(value) for key, value in data.items()}
        elif isinstance(data, list):
            return [self.replace_na_with_empty(item) for item in data]
        elif isinstance(data, str) and data == 'NA':
            return ''  # Replace 'NA' with an empty string
        else:
            return data
