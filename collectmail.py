import requests
from bs4 import BeautifulSoup
import re
import tldextract
from urllib.parse import urljoin
import time

start_url = "https://www.example.com"
domain = tldextract.extract(start_url).registered_domain

emails = set()
visited_urls = set()
urls_to_visit = set([start_url])

def get_emails_from_text(text):
    return set(re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text))

def extract_links(soup, base_url):
    links = set()
    for a_tag in soup.find_all('a', href=True):
        href = a_tag['href']
        full_url = urljoin(base_url, href)
        if tldextract.extract(full_url).registered_domain == domain:
            links.add(full_url)
    return links

while urls_to_visit:
    current_url = urls_to_visit.pop()
    if current_url in visited_urls:
        continue
    visited_urls.add(current_url)
    
    print(f"Processed URL: {current_url}")  
    try:
        response = requests.get(current_url, timeout=10)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')

        new_emails = get_emails_from_text(soup.text)
        new_emails = new_emails - emails  
        emails.update(new_emails)
        

        with open("emails.txt", "a") as file:
            for email in new_emails:
                file.write(email + "\n")
                print(f"Find new email address: {email}")  

        new_links = extract_links(soup, current_url)
        urls_to_visit.update(new_links - visited_urls)
        
        time.sleep(1)
        
    except (requests.RequestException, KeyboardInterrupt) as e:
        print(f"Error or stopped: {e}")
        break

print(f"{len(emails)} email addresses into 'emails.txt' saved")
