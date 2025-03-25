import scrapy
import json
from datetime import datetime
from urllib.parse import urlencode, urlparse, parse_qs, urlunparse, urljoin
import hashlib
from bs4 import BeautifulSoup
import re



class DetailsSpider(scrapy.Spider):
    name = "details"
    allowed_domains = ["www.timesjobs.com"]
    start_urls = ["https://www.timesjobs.com/candidate/job-search.html"]
    
    def extract_experience_range(self, text):
        parts = text.split("to")
        from_experience = parts[0].strip() if len(parts) > 0 else ""
        to_experience = parts[1].strip() if len(parts) > 1 else ""
        return from_experience, to_experience
    
    JobTypes = {
        'Full Time': 'Full time',
        'Part Time': 'Part time',
        'INTERNSHIP_/_PROJECTS': 'Internship',
        'Freelance': 'Freelance'
    }

    def parse(self, response):
        # Extract category URLs
        category_urls = response.xpath('//ul[@id="showIndustry"]/li/a/@href').extract()
        for category_url in category_urls:
            full_url = urljoin("https://www.timesjobs.com", category_url)
            yield scrapy.Request(url=full_url, callback=self.parse_listing)

    def parse_listing(self, response):
        # Extract job URLs from the current page
        job_urls = response.xpath('//h2[@class="heading-trun"]/a/@href').extract()

        # Process job links
        for job_url in job_urls:
            full_job_url = urljoin("https://www.timesjobs.com", job_url)
            yield scrapy.Request(url=full_job_url, callback=self.parse_job)

        # Check if jobs are found; stop if none exist
        if not job_urls:
            self.logger.info(f"No jobs found on {response.url}. Stopping pagination.")
            return

        # Pagination logic
        current_sequence = response.meta.get('sequence', 1)  # Default sequence is 1
        next_sequence = current_sequence + 1  # Increment sequence for the next page

        # Modify the query parameters for the next page
        parsed_url = urlparse(response.url)
        query_params = parse_qs(parsed_url.query)

        # Update parameters for pagination
        query_params.update({
            'pDate': ['Y'],
            'sequence': [str(next_sequence)],
            'startPage': ['1']
        })

        # Rebuild the next page URL
        next_page_url = urlunparse(parsed_url._replace(query=urlencode(query_params, doseq=True)))

        # Log for debugging
        self.logger.info(f"Current Page: {current_sequence}, Next Page URL: {next_page_url}")

        # Schedule the next page request
        yield scrapy.Request(
            url=next_page_url,
            callback=self.parse_listing,
            meta={'sequence': next_sequence}  # Pass updated sequence for tracking
        )


    def parse_job(self, response):
        job_url = response.url
        job_id = hashlib.md5(job_url.encode('utf-8')).hexdigest()
        designation = response.xpath('//h1[@class="jd-job-title"]/text()').get(default='').strip()
        
        job_posting_data = {}
        ld_json_scripts = response.xpath('//script[@type="application/ld+json"]/text()').getall()
        for script in ld_json_scripts:
            try:
                data = json.loads(script)
                if data.get("@type") == "JobPosting":
                    job_posting_data = data
                    break
            except json.JSONDecodeError:
                continue

        experience_text = response.xpath('//i[@class="srp-icons experience"]/following-sibling::text()').get(default='').strip()
        experience_from, experience_to = self.extract_experience_range(experience_text)

        job_function = response.xpath('//label[text()="Job Function:"]/following-sibling::span/text()').get(default='').strip()
        industry = response.xpath('//label[text()="Industry:"]/following-sibling::span/text()').get(default='').strip()
        skills = response.xpath('//div[@class="jd-sec job-skills clearfix"]/div/span/a/text()').extract()

        about_raw_html = response.xpath('//div[@class="jd-sec jd-hiring-comp"]').get()
        if about_raw_html:
            soup = BeautifulSoup(about_raw_html, "html.parser")
            for tag in soup.find_all(True):
                tag.attrs = {}
            about_html = soup.prettify()  
        else:
            about_html = ""

        about_raw_text = response.xpath('//div[@class="jd-sec jd-hiring-comp"]/text()').getall()
        about_text = ''.join([line.strip() for line in about_raw_text if line.strip()])

        qualification_raw_html = response.xpath('//label[text()="Qualification:"]/following-sibling::span').get()
        if qualification_raw_html:
            soup = BeautifulSoup(qualification_raw_html, "html.parser")
            for tag in soup.find_all(True):
                tag.attrs = {}
            qualification_html = soup.prettify()
        else:
            qualification_html = ""

        qualification_raw_text = response.xpath('//label[text()="Qualification:"]/following-sibling::span//li/text()').extract()
        qualification_text = [text.strip() for text in qualification_raw_text if text.strip()]

        job_detail_raw_html = response.xpath('//div[@class="jd-desc job-description-main"]').get()
        if job_detail_raw_html:
            soup = BeautifulSoup(job_detail_raw_html, "html.parser")
            for tag in soup.find_all(True):
                tag.attrs = {}
            job_detail_html = soup.prettify()
        else:
            job_detail_html = ""

        job_detail_raw_text = response.xpath('//div[@class="jd-desc job-description-main"]//text()').getall()
        job_detail_text = ' '.join([text.strip() for text in job_detail_raw_text if text.strip()])

        job_details = {
            "id": job_id,
            "designation": designation,
            "company": job_posting_data.get("identifier", {}).get("name", ""),
            "industry": industry,
            "jobFunction": job_function,
            "skills": skills,
            "salary": {
                "min": {"amount": job_posting_data.get("baseSalary", {}).get("value", {}).get("minValue", ""), "currency": "INR"},
                "max": {"amount": job_posting_data.get("baseSalary", {}).get("value", {}).get("maxValue", ""), "currency": "INR"},
                "frequency": job_posting_data.get("baseSalary", {}).get("unitText", ""),
                "description": job_posting_data.get("baseSalary", {}).get("description", "")
            },
            "location": {
                "area": '',
                "city": job_posting_data.get("jobLocation", {}).get("address", {}).get("addressLocality", ""),
                "state": job_posting_data.get("jobLocation", {}).get("address", {}).get("addressRegion", ""),
                "country": job_posting_data.get("jobLocation", {}).get("address", {}).get("addressCountry", "")
            },
            "postedAt": job_posting_data.get("datePosted", ""),
            "scrapedAt": datetime.utcnow().isoformat(),
            "applyUrls": {
                "jobUrl": job_url,
                "externalUrl": job_posting_data.get("hiringOrganization", {}).get("sameAs", "")
            },
            "jobType": self.JobTypes.get(job_posting_data.get("employmentType", ""), job_posting_data.get("employmentType", "")),  
            "workModel": "",
            "experience": {
                "range": {"from": experience_from, "to": experience_to},
                "level": ""
            },
            "postedBy": {
                "url": "",
                "name": job_posting_data.get("hiringOrganization", {}).get("name", "")
            },
            "applicants": "",
            "about": {
                "text": about_text,      # Clean text version of "about" section
                "html": about_html       # Beautified HTML of "about" section
            },
            "jobDetail": {
                "text": job_detail_text, # Clean text version of "job details"
                "html": job_detail_html  # Beautified HTML of "job details"
            },
            "qualification": {
                "text": qualification_text, 
                "html": qualification_html  
            },
            "isBlackListed": False,
            "isExpired": False if not job_posting_data.get("validThrough") else datetime.strptime(job_posting_data["validThrough"], "%Y-%m-%d").date() < datetime.utcnow().date(),
        }
        
        data_to_insert = {
                'portal': 'Timesjobs',
                'isDumped': False,
                'rawData': job_details,
            }
        yield data_to_insert

    def extract_experience_range(self, text):
        experience_values = re.findall(r'\d+', text)
        
        from_experience = experience_values[0] if len(experience_values) > 0 else ""
        to_experience = experience_values[1] if len(experience_values) > 1 else ""
        
        return from_experience, to_experience