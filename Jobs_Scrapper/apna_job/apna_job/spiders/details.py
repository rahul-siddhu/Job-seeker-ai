import scrapy
import json
from datetime import datetime
from html import unescape
import re

class DetailsSpider(scrapy.Spider):
    name = "details"
    allowed_domains = ["apna.co"]
    start_urls = ["https://production.apna.co/user-profile-orchestrator/public/v1/jobs/?page=1&page_size=15"]

    headers = {
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'en-US,en;q=0.9',
        'origin': 'https://apna.co',
        'priority': 'u=1, i',
        'referer': 'https://apna.co/',
        'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        'Cookie': 'GCLB=COHnwL3VjfOicRAD'
    }
    
    WorkModels =  {
	'Work from Office' : 'In Office',
	'FromHome' : 'From Home',
	'Hybrid' : 'Hybrid',
    'Field Job' : 'Field Job'
    }
    
    
    def clean_text(self, raw_text):
        """Cleans and normalizes the raw text."""
        if not raw_text:
            return ""
        # Unescape HTML entities
        clean_text = unescape(raw_text)
        # Replace non-breaking spaces and normalize whitespace
        clean_text = clean_text.replace('\xa0', ' ')
        clean_text = re.sub(r'\s+', ' ', clean_text)
        # Strip leading/trailing spaces
        return clean_text.strip()

    def generate_html_from_text(self, text):
        """Converts plain text into simple HTML format."""
        if not text:
            return ""
        # Replace line breaks with <br> tags for HTML format
        html_content = text.replace('\n', '<br>')
        return f"<div>{html_content}</div>"

    def parse(self, response):
        # Load the initial response JSON
        data = json.loads(response.text)
        
        # Extract the count and calculate the total pages
        count = data.get('count', 0)
        page_size = 15
        total_pages = (count // page_size) + (1 if count % page_size > 0 else 0)

        # Schedule requests for each page
        for page in range(1, total_pages + 1):
            next_page_url = f"https://production.apna.co/user-profile-orchestrator/public/v1/jobs/?page={page}&page_size={page_size}"
            yield scrapy.Request(next_page_url, headers=self.headers, callback=self.parse_jobs)

    def parse_jobs(self, response):
        # Parse JSON data for jobs
        data = json.loads(response.text)
        jobs = data.get('results', {}).get('jobs', [])
        today = datetime.utcnow().date()
        for job in jobs:
            
            expiry_date_str = job.get('expiry', '')  
            is_expired = False  
            
            if expiry_date_str:
                expiry_date = datetime.strptime(expiry_date_str, "%Y-%m-%d").date()
                is_expired = expiry_date <= today
            
            description_text = self.clean_text(job.get('description', ''))
            description_html = self.generate_html_from_text(job.get('description', ''))
                
            work_model_key = job['ui_tags'][0]['text'] if job['ui_tags'] else ''
            work_model_mapped = self.WorkModels.get(work_model_key, '')  
                    
            job_details = {
                "id": job.get('id', ''),
                "designation": job.get('title', ''),
                "company": job['organization']['name'],
                "industry": job['department']['name'],
                "jobFunction": job['category'],
                "skills": job.get('skills', []),
                "salary": {
                    "min": {
                        "amount": job.get('fixed_min_salary', ''),
                        "currency": "INR"
                    },
                    "max": {
                        "amount": job.get('fixed_max_salary', ''),
                        "currency": "INR"
                    },
                    "frequency": job.get('salaryFrequency', 'monthly'),
                    "description": ''
                },
                "location": {
                    "area": job['address']['area'],
                    "city": job['address']['city']['name'],
                    "state": '',
                    "country": ''
                },
                "postedAt": job.get('created_on', ''),
                "scrapedAt": datetime.utcnow().isoformat(),
                "applyUrls": {
                    "jobUrl": job.get('public_url', ''),
                    "externalUrl": job.get('externalApplyUrl', '')
                },
                "jobType": job['ui_tags'][1]['text'],
                "workModel": work_model_mapped,
                "experience": {
                    "range": {
                        "from": job.get('min_experience', ''),
                        "to": job.get('max_experience', '')
                    },
                    "level": ''
                },
                "postedBy": {
                    "url": job.get('postedByUrl', ''),
                    "name": job.get('postedByName', '')
                },
                "applicants": '',
                "about": {
                    "text": '',
                    "html": ''
                },
                "jobDetail": {
                    "text": description_text,
                    "html": description_html
                },
                "qualification": {
                    "text": job.get('education', ''),
                    "html": job.get('education', '')
                },
                "isBlackListed":  False,
                "isExpired": is_expired
            }
            data_to_insert = {
                'portal': 'Apna',
                'isDumped': False,
                'rawData': job_details,
            }
            yield data_to_insert
