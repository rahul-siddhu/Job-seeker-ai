# import json
# import time
# from selenium import webdriver
# from urllib.parse import urlparse
# import re
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from bs4 import BeautifulSoup
# from selenium.common.exceptions import TimeoutException, WebDriverException

# def extract_links(html_content):
#     soup = BeautifulSoup(html_content, "html.parser")
#     links = [a["href"] for a in soup.find_all("a", href=True)]
#     return links

# def isPrefix(link, prefix, author):
#     if(link.startswith(prefix)):
#         return True
#     flag=False
#     for i in range(0, len(link)):
#         j=0
#         k=i
#         while(j<len(author)):
#             if(link[i]==author[j]):
#                 j+=1
#                 i+=1
#             else:
#                 i=k
#                 break
#         if(j==len(author)):
#             flag=True
#             break
#     return flag

# def setup_driver():
#     options = webdriver.ChromeOptions()
#     # Add these options to improve reliability
#     options.add_argument("--disable-dev-shm-usage")
#     options.add_argument("--no-sandbox")
#     options.add_argument("--disable-gpu")
#     options.add_argument("--page-load-strategy=eager")  # Don't wait for all resources
#     # Uncomment below for headless operation
#     # options.add_argument("--headless")
    
#     driver = webdriver.Chrome(options=options)
#     # Set page load timeout to 30 seconds
#     driver.set_page_load_timeout(30)
#     return driver

# def extract_topics(website, class_name, i, max_retries=3, retry_delay=2):
#     # Extract domain name from website URL
#     parsed_url = urlparse(website)
#     domain_name = re.sub(r'^www\.', '', parsed_url.netloc).split('.')[0]  # Remove 'www.' and get main domain

#     # Set up Selenium WebDriver
#     driver = setup_driver()
    
#     blogs = []
#     retry_count = 0
    
#     while retry_count < max_retries:
#         try:
#             driver.get(website)
            
#             # Wait for elements to be present with shorter timeout
#             WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, class_name)))
            
#             # Find all blog post elements
#             blog_elements = driver.find_elements(By.CLASS_NAME, class_name)
#             print(f"Found {len(blog_elements)} elements with class '{class_name}'")
            
#             limit = 10
#             for element in blog_elements:
#                 if limit == 0:
#                     break
#                 limit -= 1
                
#                 try:
#                     links = extract_links(element.get_attribute("outerHTML"))
#                     # Removing duplicate and unnecessary links
#                     required_links = set()
#                     for link in links:
#                         if not isPrefix(link, "https", "/authors/"):
#                             required_links.add(link)
                    
#                     for link in required_links:
#                         full_link = "https://www.digitalocean.com" + link
#                         blogs.append({"link": full_link})
#                 except Exception as e:
#                     print(f"Error processing element: {e}")
#                     continue
            
#             # If we got here without exceptions, break the retry loop
#             break
        
#         except TimeoutException:
#             retry_count += 1
#             print(f"Timeout on {website}. Retry {retry_count}/{max_retries}")
#             if retry_count < max_retries:
#                 time.sleep(retry_delay)
#         except Exception as e:
#             print(f"Error accessing {website}: {e}")
#             break
    
#     driver.quit()
    
#     if not blogs:
#         print("No blog links found. Check the class name or website structure.")
    
#     file_name = f"Z:\\Joblo.ai\\jobloai\\Blogs scrapper\\data\\{domain_name}_links{str(i)}.json"

#     with open(file_name, "w") as file:
#         json.dump(blogs, file, indent=4)
    
#     print(f"Blog data saved to {file_name}")
#     return blogs

# def extract_blog_content(website, links, class_name, i, max_retries=3, retry_delay=5):
#     if not links:
#         print("No links found, skipping content extraction.")
#         return {}
    
#     parsed_url = urlparse(website)
#     domain_name = re.sub(r'^www\.', '', parsed_url.netloc).split('.')[0]
    
#     driver = setup_driver()
#     data_list = {}
    
#     for link_info in links:
#         link = link_info['link']
#         print(f"Processing: {link}")
        
#         retry_count = 0
#         while retry_count < max_retries:
#             try:
#                 driver.get(link)
#                 # Shorter wait time
#                 WebDriverWait(driver, 15).until(EC.presence_of_all_elements_located((By.CLASS_NAME, class_name)))
                
#                 elements = driver.find_elements(By.CLASS_NAME, class_name)
#                 if elements:
#                     data_list[link] = elements[0].get_attribute("outerHTML")
#                     print(f"Successfully extracted content from {link}")
#                 else:
#                     print(f"No elements with class '{class_name}' found on {link}")
                
#                 # If successful, break the retry loop
#                 break
                
#             except TimeoutException:
#                 retry_count += 1
#                 print(f"Timeout on {link}. Retry {retry_count}/{max_retries}")
#                 if retry_count < max_retries:
#                     time.sleep(retry_delay)
#             except WebDriverException as e:
#                 print(f"Browser error on {link}: {e}")
#                 # For browser errors, increase retry delay
#                 time.sleep(retry_delay * 2)
#                 retry_count += 1
#             except Exception as e:
#                 print(f"Unexpected error processing {link}: {e}")
#                 break
        
#         # Save progress after each successful link processing
#         # if link in data_list:
#         #     temp_file_name = f"{domain_name}_progress.json"
#         #     with open(temp_file_name, "w") as file:
#         #         json.dump(data_list, file, indent=4)
    
#     driver.quit()
    
#     file_name = f"Z:\\Joblo.ai\\jobloai\\Blogs scrapper\\data\\{domain_name}{str(i)}.json"

#     with open(file_name, "w") as file:
#         json.dump(data_list, file, indent=4)
    
#     print(f"Blog content saved to {file_name}")
#     return data_list
# sites = [
#     # {
#     #     "site": "https://www.digitalocean.com/blog/tags/cloud-education",
#     #     "class_blog": "SidebarLayoutStyles__StyledSidebarLayoutContainer-sc-c44944e2-1",
#     #     "class_title": "BlogCardStyles__StyledBlogCard-sc-24e6ba9f-0"
#     # },
#     {
#         "site": "https://www.digitalocean.com/blog/tags/engineering",
#         "class_blog": "Layout__StyledLayout-sc-3a10f19e-0",
#         "class_title": "BlogCardStyles__StyledBlogCard-sc-24e6ba9f-0"
#     }
# ]
# if __name__ == "__main__":
#     for i in range(0, len(sites)):
#         site=sites[i]
#         try:
#             links = extract_topics(site['site'], site['class_title'], i)
#             extract_blog_content(site['site'], links, site['class_blog'], i)
#             print("*" * 50)
#         except Exception as e:
#             print(f"Error processing site {site['site']}: {e}")
import time
from selenium import webdriver
from urllib.parse import urlparse
import re
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from selenium.common.exceptions import TimeoutException, WebDriverException
from pymongo import MongoClient

def connect_mongo():
    client = MongoClient("mongodb+srv://lil_boo:lil_boo22@cluster0.qoqzo.mongodb.net/")  # Update with your MongoDB URI if needed
    db = client["blogs"]  # Database name
    return db["digital_ocean"]  # Collection name

def extract_links(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    return [a["href"] for a in soup.find_all("a", href=True)]

def isPrefix(link, prefix, author):
    if link.startswith(prefix):
        return True
    flag = False
    for i in range(len(link)):
        j, k = 0, i
        while j < len(author) and i < len(link) and link[i] == author[j]:
            j += 1
            i += 1
        if j == len(author):
            flag = True
            break
    return flag

def setup_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    options.add_argument("--page-load-strategy=eager")
    driver = webdriver.Chrome(options=options)
    driver.set_page_load_timeout(30)
    return driver

def extract_topics(website, class_name, max_retries=3, retry_delay=2):
    parsed_url = urlparse(website)
    domain_name = re.sub(r'^www\\.', '', parsed_url.netloc).split('.')[0]
    driver = setup_driver()
    blogs = []
    retry_count = 0
    while retry_count < max_retries:
        try:
            driver.get(website)
            WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, class_name)))
            blog_elements = driver.find_elements(By.CLASS_NAME, class_name)
            print(f"Found {len(blog_elements)} elements with class '{class_name}'")
            
            limit = 10
            for element in blog_elements:
                if limit == 0:
                    break
                limit -= 1
                try:
                    links = extract_links(element.get_attribute("outerHTML"))
                    required_links = {link for link in links if not isPrefix(link, "https", "/authors/")}
                    for link in required_links:
                        full_link = "https://www.digitalocean.com" + link
                        blogs.append({"link": full_link, "domain": domain_name})
                except Exception as e:
                    print(f"Error processing element: {e}")
                    continue
            break
        except TimeoutException:
            retry_count += 1
            print(f"Timeout on {website}. Retry {retry_count}/{max_retries}")
            if retry_count < max_retries:
                time.sleep(retry_delay)
        except Exception as e:
            print(f"Error accessing {website}: {e}")
            break
    driver.quit()
    if not blogs:
        print("No blog links found. Check the class name or website structure.")
    return blogs

def extract_blog_content(links, class_name, max_retries=3, retry_delay=5):
    if not links:
        print("No links found, skipping content extraction.")
        return
    
    driver = setup_driver()
    collection = connect_mongo()
    for link_info in links:
        link = link_info['link']
        print(f"Processing: {link}")
        retry_count = 0
        while retry_count < max_retries:
            try:
                driver.get(link)
                WebDriverWait(driver, 15).until(EC.presence_of_all_elements_located((By.CLASS_NAME, class_name)))
                elements = driver.find_elements(By.CLASS_NAME, class_name)
                if elements:
                    content = elements[0].get_attribute("outerHTML")
                    collection.insert_one({"link": link, "content": content})
                    print(f"Stored content from {link}")
                else:
                    print(f"No elements with class '{class_name}' found on {link}")
                break
            except TimeoutException:
                retry_count += 1
                print(f"Timeout on {link}. Retry {retry_count}/{max_retries}")
                if retry_count < max_retries:
                    time.sleep(retry_delay)
            except WebDriverException as e:
                print(f"Browser error on {link}: {e}")
                time.sleep(retry_delay * 2)
                retry_count += 1
            except Exception as e:
                print(f"Unexpected error processing {link}: {e}")
                break
    driver.quit()

sites = [
    {
        "site": "https://www.digitalocean.com/blog/tags/engineering",
        "class_blog": "Layout__StyledLayout-sc-3a10f19e-0",
        "class_title": "BlogCardStyles__StyledBlogCard-sc-24e6ba9f-0"
    }
]

if __name__ == "__main__":
    for site in sites:
        try:
            links = extract_topics(site['site'], site['class_title'])
            extract_blog_content(links, site['class_blog'])
            print("*" * 50)
        except Exception as e:
            print(f"Error processing site {site['site']}: {e}")
