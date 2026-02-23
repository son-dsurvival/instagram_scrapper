import scrapy
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time

item = {
        "post_url": [],
        "caption": [],
        "likes": [],
        "comments": []
    }
class InstaSpiderSpider(scrapy.Spider):
    name = "insta_spider"
    allowed_domains = ["instagram.com"]
    start_urls = ["https://www.instagram.com/oolufemisayo/"]  # Replace with a public profile

    def __init__(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--log-level=3")
        chrome_options.add_argument("--enable-unsafe-webgl")
  # clean logs
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    def parse(self, response):
        self.driver.get(response.url)
        time.sleep(120)  # Wait for profile content to load

        post_links = self.driver.find_elements(By.CSS_SELECTOR, 'article a')
        links = [a.get_attribute("href") for a in post_links if a.get_attribute("href")]

        for link in links[:10]:  # Limit for testing; remove [:10] for all posts
            yield scrapy.Request(url=link, callback=self.parse_post)

    

    def parse_post(self, response):
        self.driver.get(response.url)
        time.sleep(120)  # Wait for post to load

        item["post_url"].append(response.url)


        try:
            # Get caption (first <span> inside <div role="button">)
            caption_element = self.driver.find_element(By.CSS_SELECTOR, 'div[role="button"] span')
            item["caption"] .append(caption_element.text)
        except:
            item["caption"].append("No caption")

        try:
            # Get likes (or views)
            like_button = self.driver.find_element(By.XPATH, '//section/div/div/span/a/span')
            item["likes"].append(like_button.text)
        except:
            try:
                # For video views instead of likes
                views = self.driver.find_element(By.XPATH, '//section/div/span/span')
                item["likes"].append(views.text + " views")
            except:
                item["likes"].append("Not found")

        try:
            # Get top-level comments
            comment_elements = self.driver.find_elements(By.XPATH, '//ul/div/li/div/div/div/div/span')
            item["comments"].append( [c.text for c in comment_elements[1:]])  # Skip first (caption repeated)
        except:
            item["comments"].append([])

    def closed(self, reason):
        self.driver.quit()
        print(item)
    
