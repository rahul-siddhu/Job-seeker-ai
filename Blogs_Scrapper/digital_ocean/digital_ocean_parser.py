# import json
# from bs4 import BeautifulSoup
# from digital_ocean import sites

# # Use raw string or replace backslashes with forward slashes
# json_file_path = r"Z:\Joblo.ai\jobloai\Blogs scrapper\data\digitalocean0.json"

# # Open and read the JSON file
# with open(json_file_path, "r", encoding="utf-8") as file:
#     data = json.load(file)  # Load JSON into a Python dictionary

# data_list = []

# eq=""

# for blog_link, blog in data.items():
#     # Parse JSON content
#     # blog_html = json.loads(blog)["html"]
    
#     # Convert HTML string into BeautifulSoup object
#     soup = BeautifulSoup(blog, "html.parser")

#     # Extract required data
#     blog_data = {
#         "heading": soup.find("h1", class_="HeadingStyles__StyledH1-sc-73f0758c-0").get_text(strip=True) if soup.find("h1", class_="HeadingStyles__StyledH1-sc-73f0758c-0") else None,
#         "author": soup.find("a", class_="LinkInlinestyles-sc-18du0ds-0").get_text(strip=True) if soup.find("a", class_="LinkInlinestyles-sc-18du0ds-0") else None,
#         "postedAt": soup.find("div", class_="BlogPickStyles__StyledDate-sc-6d4f3ac1-0").get_text(strip=True) if soup.find("div", class_="BlogPickStyles__StyledDate-sc-6d4f3ac1-0") else None, 
#         "portal": "Digital Ocean",
#         "category": sites[0]["site"].split("/")[-1],
#         "domain": "https://www.digitalocean.com",
#         "link": blog_link,
#         "content": soup.find("div", class_="Markdownstyles-sc-dd1icp-0").get_text(strip=True) if soup.find("div", class_="Markdownstyles-sc-dd1icp-0") else None
#     }
#     data_list.append(blog_data)

# # Save as JSON
# with open("parsed_digital_ocean.json", "w", encoding="utf-8") as json_file:
#     json.dump(data_list, json_file, indent=4, ensure_ascii=False)

# print("Blog data saved successfully!")
from pymongo import MongoClient
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from digital_ocean import sites  # Assuming this contains category details

# Connect to MongoDB
client = MongoClient("mongodb+srv://lil_boo:lil_boo22@cluster0.qoqzo.mongodb.net/")
db = client["blogs"]  # Database
raw_collection = db["digital_ocean"]  # Collection with raw HTML data
parsed_collection = db["parsed_digital_ocean"]  # New collection for structured data

# Fetch all blog posts from the database
raw_blogs = raw_collection.find()

data_list = []
for raw_blog in raw_blogs:
    blog_link = raw_blog["link"]
    blog_html = raw_blog["content"]
    parsed_url = urlparse(blog_link)
    
    soup = BeautifulSoup(blog_html, "html.parser")
    
    # Extract structured data
    blog_data = {
        "heading": soup.find("h1", class_="HeadingStyles__StyledH1-sc-73f0758c-0").get_text(strip=True) if soup.find("h1", class_="HeadingStyles__StyledH1-sc-73f0758c-0") else None,
        "author": soup.find("a", class_="LinkInlinestyles-sc-18du0ds-0").get_text(strip=True) if soup.find("a", class_="LinkInlinestyles-sc-18du0ds-0") else None,
        "postedat": soup.find("div", class_="BlogPickStyles__StyledDate-sc-6d4f3ac1-0").get_text(strip=True) if soup.find("div", class_="BlogPickStyles__StyledDate-sc-6d4f3ac1-0") else None,
        "portal": "Digital Ocean",
        "category": sites[0]["site"].split("/")[-1],
        "domain": parsed_url.netloc,
        "link": blog_link,
        "content": soup.find("div", class_="Markdownstyles-sc-dd1icp-0").get_text(strip=True) if soup.find("div", class_="Markdownstyles-sc-dd1icp-0") else None
    }
    
    # Store in MongoDB
    parsed_collection.insert_one(blog_data)
    data_list.append(blog_data)

print(f"Successfully stored {len(data_list)} parsed blog posts in MongoDB.")
