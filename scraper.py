import requests
from bs4 import BeautifulSoup
import json
import time 

# --- 1. SET YOUR TARGET: ***CRITICAL STEP: CHANGE THIS!*** ---
# We are replacing the generic placeholder with a specific search URL.
# Note: Naukri is very aggressive against scrapers. If this fails, use a large MNC career page.
TARGET_URL = 'https://www.naukri.com/fresher-jobs-in-india?src=nav&lang=en' # Targeting the Fresher Jobs page on Naukri

# --- 2. DEFINE SELECTORS: ***CRITICAL STEP: UPDATED FOR NAUKRI-LIKE STRUCTURES!*** ---
# This selector finds the main box/container for a single job listing.
# Note: This is an educated guess based on common card structures.
JOB_CARD_SELECTOR = 'div.srp-jobtuple-wrapper' 

# These selectors find the individual data points *inside* the JOB_CARD_SELECTOR.
TITLE_SELECTOR = 'a.title'
COMPANY_SELECTOR = 'a.comp-name'
LINK_SELECTOR = 'a.title' # The title link is the application link
# --- --------------------------------------- ---

def run_scraper():
    """Fetches web data and attempts to extract job-like structures."""
    print(f"Starting connection test for: {TARGET_URL}")
    print(f"Goal: Scraping Freshers Jobs in India.")
    
    scraped_items = []

    try:
        # User-Agent to mimic a regular browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # Add a polite delay to avoid overwhelming the server
        time.sleep(3) # Increased delay for a major site like Naukri
        
        # 1. Fetch the page content
        response = requests.get(TARGET_URL, headers=headers, timeout=20)
        response.raise_for_status() # Check for request errors

        # 2. Parse the content
        soup = BeautifulSoup(response.content, 'html.parser')

        # 3. Find all the main items 
        all_items = soup.select(JOB_CARD_SELECTOR) 

        if not all_items:
            print(f"Error: Found 0 items using the selector '{JOB_CARD_SELECTOR}'. This usually means the selector is wrong or the content is dynamic (JavaScript loaded).")
            print("Action needed: If this fails, you MUST target a simpler website, or manually inspect Naukri for a new selector.")
            return []

        # 4. Loop through found items and extract data
        for index, item in enumerate(all_items):
            try:
                # --- EXTRACTING DATA ---
                title = item.select_one(TITLE_SELECTOR).text.strip()
                company = item.select_one(COMPANY_SELECTOR).text.strip()
                
                # Extract the URL/Link
                link_tag = item.select_one(LINK_SELECTOR)
                link = link_tag['href'] if link_tag and link_tag.has_attr('href') else '#'
                
                # Clean up and append the data
                scraped_items.append({
                    "id": index + 1,
                    "title": title.strip('"'),
                    "company": company,
                    "location": "India - Fresher", 
                    "description": f"Scraped from Naukri (Fresher). Apply before 30 days.",
                    "link": link # Use the direct link
                })

            except AttributeError:
                # Skip items if structure is unexpectedly missing a piece
                continue
            
        print(f"Scraping completed. Found {len(scraped_items)} items.")
        return scraped_items

    except requests.exceptions.RequestException as e:
        print(f"Failed to connect to {TARGET_URL}: {e}")
        return []

# --- 5. EXPORT AND FINALIZE ---
if __name__ == "__main__":
    real_job_data = run_scraper()
    
    # Save the data to a JSON file
    with open('real_jobs.json', 'w', encoding='utf-8') as f:
        json.dump(real_job_data, f, ensure_ascii=False, indent=4)
        
    print("\nData saved to real_jobs.json. Ready for copy-paste.")
    
    # Print the JSON content to the console for easy copy-paste
    print("\n\n--- COPY THIS SECTION INTO index.html ---")
    print(json.dumps(real_job_data, ensure_ascii=False, indent=4))
    print("----------------------------------------\n")
