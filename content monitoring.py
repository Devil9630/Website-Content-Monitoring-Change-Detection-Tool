import requests
import time
import difflib
import re
from datetime import datetime
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# Function to get the content of a website
def get_website_content(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Check if the website is reachable
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None

# Function to clean and simplify content for comparison
def clean_content(content):
    # Remove script and style elements
    content = re.sub(r'<script.*?>.*?</script>', '', content, flags=re.DOTALL)
    content = re.sub(r'<style.*?>.*?</style>', '', content, flags=re.DOTALL)
    # Remove all HTML tags
    content = re.sub(r'<.*?>', '', content)
    # Normalize whitespace
    content = re.sub(r'\s+', ' ', content)
    return content.strip()

# Function to find links on the base page (not recursive)
def find_links(url):
    """Fetch a page and find all links within it. Returns a set of absolute URLs."""
    links = set()
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        for link in soup.find_all('a', href=True):
            absolute_link = urljoin(url, link['href'])
            links.add(absolute_link)
    except Exception as e:
        print(f"Error fetching links from {url}: {e}")
    return links

# Main monitoring function
def monitor_pages(urls, interval=30, no_change_interval=300):
    """Monitor a list of URLs for changes."""
    content_history = {}
    last_change_time = datetime.now()

    while True:
        for url in urls:
            print(f"Checking {url}")
            raw_content = get_website_content(url)
            if raw_content:
                current_content = clean_content(raw_content)
                previous_content = content_history.get(url)
                if previous_content and current_content != previous_content:
                    print(f"Change detected in content of {url}")
                    # Show differences (simplified)
                    print("Change detected, content updated.")
                content_history[url] = current_content
            else:
                print(f"No content retrieved from {url}")
        
        current_time = datetime.now()
        if (current_time - last_change_time).seconds >= no_change_interval:
            print("No changes detected in the monitored period.")
            last_change_time = current_time

        time.sleep(interval)

# Example usage
base_url = 'https://smgroupindia.org'
links = find_links(base_url)
print(f"Monitoring {len(links)} pages...")
monitor_pages(links)
