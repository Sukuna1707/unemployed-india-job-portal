import requests
from bs4 import BeautifulSoup
import json

# --- 1. SET YOUR TARGET: ***CRITICAL STEP*** ---
# 1. Replace the URL below with the *actual* search results page URL from a website (e.g., Indeed, Naukri, or a specific company's career page).
# 2. Always check the target website's robots.txt file for scraping permissions (add /robots.txt to the root domain).
TARGET_URL = 'https://studentscircles.com/jobs/'  # TARGET URL: Wellfound Jobs
# --- --------------------------------------- ---

def run_scraper():
    """Fetches job listings, extracts data, and saves it to a JSON file."""
    print(f"Starting job scraper for: {TARGET_URL}")
    
    scraped_jobs = []

    try:
        # Send a request to fetch the HTML content
        # Use a user-agent to pretend you are a regular browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        # Adding a small, polite delay between requests to avoid overwhelming the server
        response = requests.get(TARGET_URL, headers=headers, timeout=15)
        response.raise_for_status() # Raise an error for bad status codes (4xx or 5xx)

        # Parse the HTML content
        soup = BeautifulSoup(response.content, 'html.parser')

        # --- 2. FIND JOB CARDS (THIS SELECTOR MUST BE CUSTOMIZED!) ---
        # NOTE: Wellfound uses a highly dynamic website structure (JavaScript/React). 
        # A simple 'requests.get' may only fetch the framework, not the jobs themselves.
        # You will likely need to use Selenium/Playwright (more complex tools) for full success.
        # We will try a common container class here, but be prepared to check the output!
        JOB_CARD_SELECTOR = 'div[data-test="JobCard"]' # Targeting a plausible data attribute for modern sites
        job_listings = soup.select(JOB_CARD_SELECTOR) 

        if not job_listings:
            print(f"Error: Could not find any job listings using the selector '{JOB_CARD_SELECTOR}'.")
            print("Action Needed: If the job list is empty, Wellfound is likely loading jobs with JavaScript.")
            print("You must inspect the page source to find the correct selector, or switch to a tool that handles JavaScript rendering.")
            return []

        # --- 3. EXTRACT DETAILS FROM EACH CARD ---
        for index, job_card in enumerate(job_listings):
            if index >= 50: # Limit to 50 jobs for simplicity
                break
            
            # --- CUSTOMIZE THESE SELECTORS FOR YOUR TARGET WEBSITE ---
            try:
                # Find the primary link/title
                title_tag = job_card.find('a', class_='styles_title_') # Example class targeting the job title link
                
                if not title_tag: continue # Skip if title not found
                
                title = title_tag.text.strip()
                
                # IMPORTANT: Wellfound links are relative. We need the full link.
                link = "https://studentscircles.com/jobs/" + title_tag['href'] if title_tag.get('href') else "#"
                
                # Extract Company Name (Often linked)
                company_tag = job_card.find('a', class_='styles_companyName') # Example class targeting company name
                company = company_tag.text.strip() if company_tag else "N/A"
                
                # Extract Location (Often a tag below the company)
                location_tag = job_card.find('div', class_='styles_location')
                location = location_tag.text.strip() if location_tag else 'N/A'

                # Extract Description Snippet (Simplifying to a placeholder as snippets are often tricky)
                description = f"Job listing summary for {title} at {company}. Check link for details."
                
                scraped_jobs.append({
                    "id": index + 1,
                    "title": title,
                    "company": company,
                    "location": location,
                    "description": description,
                    "link": link
                })

            except AttributeError as e:
                # This happens if one of the find() calls returns None, meaning the data structure changed.
                print(f"Skipping job card {index + 1} due to HTML structure issue: {e}")
                continue

    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch {TARGET_URL}: {e}")
        return []

    print(f"Scraping completed. Found {len(scraped_jobs)} jobs.")
    return scraped_jobs

# --- 4. EXPORT AND FINALIZE ---
if __name__ == "__main__":
    real_job_data = run_scraper()
    
    # Save the data to a JSON file (the format your index.html needs)
    with open('real_jobs.json', 'w', encoding='utf-8') as f:
        json.dump(real_job_data, f, ensure_ascii=False, indent=4)
        
    print("\nData saved to real_jobs.json. Ready for copy-paste.")
    
    # Optional: Print the JSON content to the console for easy copy-paste
    print("\n\n--- COPY THIS SECTION INTO index.html ---")
    print(json.dumps(real_job_data, ensure_ascii=False, indent=4))
    print("----------------------------------------\n")
