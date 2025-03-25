import scrapy
import json
import re
from datetime import datetime

class InternshalaSpider(scrapy.Spider):
    name = "details"
    allowed_domains = ["internshala.com"]
    start_urls = ["https://internshala.com/jobs-by-category/"]

    Currencies = {
        "INR": "INR",
    }

    Frequencies = {
        "HOURLY": "per hour",
        "DAILY": "per day",
        "WEEK": "per week",
        "MONTH": "per month",
        "YEAR": "yearly"
    }

    JobTypes = {
        "FULL_TIME": "Full time",
        "PART_TIME": "Part time",
        "PART_TIME, CONTRACTOR": "Part time",
        "VOLUNTEER, FULL_TIME": "Full time",
    }

    ExperienceLevels = {
        "entry_level": "Entry Level",
        "mid_level": "Mid Level",
        "senior_level": "Senior Level",
    }

    def format_datetime(self, dt):
        return dt.strftime('%Y-%m-%dT%H:%M:%S')

    def remove_html_tags(self, text):
        return scrapy.Selector(text=text).xpath("string()").get(default="").strip()

    def extract_section(self, text, delimiter="About Company:", part="before"):
        """
        Safely extracts a section of the text based on a delimiter.
        """
        if delimiter in text:
            parts = text.split(delimiter, 1)
            if part == "before":
                return parts[0].strip()
            elif part == "after":
                return parts[1].strip()
        return text.strip()  # Return the full text if delimiter is absent

    def parse(self, response):
        category_urls = response.xpath('//div[@id="job_category"]//a/@href').getall()

        if not category_urls:
            self.logger.warning(f"No category URLs found on {response.url}")
        else:
            self.logger.info(f"Found {len(category_urls)} category URLs.")
            for url in category_urls:
                full_url = response.urljoin(url)
                yield scrapy.Request(full_url, callback=self.parse_category)

    def parse_category(self, response):
        job_links = response.xpath('//a[@class="job-title-href"]/@href').getall()
        for job_url in job_links:
            full_job_url = f"https://internshala.com{job_url}"
            yield scrapy.Request(full_job_url, callback=self.parse_job)

        total_pages = response.xpath('//span[@id="total_pages"]/text()').get()
        if total_pages:
            total_pages = int(total_pages.strip())
            current_page_match = re.search(r'page-(\d+)', response.url)
            current_page = int(current_page_match.group(1)) if current_page_match else 1

            if current_page < total_pages:
                next_page = current_page + 1
                next_page_url = response.urljoin(f"{response.url.split('/page-')[0]}/page-{next_page}/")
                yield scrapy.Request(next_page_url, callback=self.parse_category)

    def parse_job(self, response):
        script = response.xpath('//script[@type="application/ld+json"]/text()').get()
        if not script:
            self.logger.warning(f"No JSON data found on {response.url}")
            return

        try:
            job_data = json.loads(script)
        except json.JSONDecodeError:
            self.logger.error(f"Invalid JSON data on {response.url}")
            return

        if job_data.get("@type") != "JobPosting":
            self.logger.warning(f"Invalid job data on {response.url}")
            return

        experience = response.xpath('//div[@class="other_detail_item job-experience-item"]/div[@class="item_body desktop-text"]/text()').get()
        applicants = response.xpath('//div[@class="applications_message"]/text()').get()

        raw_description = job_data.get("description", "")
        clean_description = self.remove_html_tags(raw_description)

        # Use helper method to extract sections, or leave empty if not available
        about_company = self.extract_section(clean_description, "About Company:", part="after") if "About Company:" in clean_description else ""
        description_without_about = self.extract_section(clean_description, "About Company:", part="before").replace('\n', '') if "About Company:" in clean_description else clean_description

        base_salary = job_data.get("baseSalary", {}).get("value", {})
        min_salary = base_salary.get("minValue", 0)
        max_salary = base_salary.get("maxValue", 0)
        salary_currency = job_data.get("baseSalary", {}).get("currency", "")

        location_data = job_data.get("jobLocation", [{}])[0].get("address", {})
        city = location_data.get("addressLocality", "")
        state = location_data.get("addressRegion", "")
        country = location_data.get("addressCountry", "")
        area = location_data.get("streetAddress", "").replace('-','')

        skills = job_data.get("skills", "")
        skills_list = [skill.strip() for skill in skills.split(",")]

        frequency = job_data.get("baseSalary", {}).get("unitText", "")
        frequency_mapped = self.Frequencies.get(frequency, "")

        job_type = job_data.get("employmentType", "")
        job_type_mapped = self.JobTypes.get(job_type, job_type)  

        experience_range = {"from": "", "to": ""}
        if experience:
            exp_values = re.findall(r'\d+', experience)
            if len(exp_values) == 2:
                experience_range = {"from": exp_values[0], "to": exp_values[1]}

        job_details = {
            "id": job_data.get("identifier", {}).get("value", ""),
            "designation": job_data.get("title", ""),
            "company": job_data.get("hiringOrganization", {}).get("name", ""),
            "industry": job_data.get("industry", ""),
            "jobFunction": "",
            "skills": skills_list,
            "salary": {
                "min": {
                    "amount": min_salary,
                    "currency": salary_currency,
                },
                "max": {
                    "amount": max_salary,
                    "currency": salary_currency,
                },
                "frequency": frequency_mapped,
                "description": ""
            },
            "location": {
                "area": area,
                "city": city,
                "state": state,
                "country": country,
            },
            "postedAt": job_data.get("datePosted", ""),
            "scrapedAt": datetime.utcnow().isoformat(),
            "applyUrls": {
                "jobUrl": response.url,
                "externalUrl": ""
            },
            "jobType": job_type_mapped,
            "workModel": "",
            "experience": {'range': experience_range, 'level': ''},
            "postedBy": {
                "url": "",
                "name": job_data.get("hiringOrganization", {}).get("name", ""),
            },
            "applicants": ''.join(filter(str.isdigit, applicants)) if applicants else '',
            "about": {
                "text": about_company.strip() if about_company else "",  # Check if "about_company" is available
                "html": self.extract_section(raw_description, "About Company:", part="after").strip() if about_company else "",  # Check if "about_company" is available
            },
            "jobDetail": {
                "text": description_without_about.strip() if description_without_about else "",  # Check if "description_without_about" is available
                "html": self.extract_section(raw_description, "About Company:", part="before").strip() if description_without_about else "",  # Check if "description_without_about" is available
            },
            "qualification": {
                "text": "",
                "html": ""
            },
            "isBlackListed": False,
            "isExpired": False
        }

        data_to_insert = {
            'portal': 'Internshala',
            'rawData': job_details,
        }

        yield data_to_insert
