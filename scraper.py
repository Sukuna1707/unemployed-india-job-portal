import requests
import json
from datetime import datetime

# --- CONFIGURATION ---
# The script now uses API endpoints to reliably fetch data from multiple sources.
# This approach is fast, reliable, and avoids anti-scraping walls.
# We are currently targeting India-based jobs from major platforms.
ALL_JOBS = []

# --- 1. DATA SOURCE FUNCTIONS ---

# === GOOGLE CAREERS ===
def fetch_google_jobs():
    """Fetches jobs directly from the Google Careers API for India."""
    try:
        url = "https://careers.google.com/api/v3/search/?location=India"
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        data = r.json()
        
        jobs = []
        for job in data.get("jobs", []):
            jobs.append({
                "title": job.get("title", "N/A"),
                "company": "Google",
                "location": job.get("locations", [{}])[0].get("display", "N/A"),
                "description": "Tech, Engineering, and Business roles at Google India.",
                "apply_link": job.get("applyUrl") or job.get("detailsUrl", "N/A")
            })
        print(f"✅ Google: Found {len(jobs)} jobs.")
        return jobs
    except Exception as e:
        print("❌ Google fetch failed (This API may change often):", e)
        return []

# === LEVER (Zoho Example) ===
def fetch_lever_jobs():
    """Fetches jobs directly from the Lever API for Zoho, filtering for India."""
    try:
        url = "https://api.lever.co/v0/postings/zoho?mode=json"
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        data = r.json()
        
        jobs = []
        for job in data:
            location = job.get("categories", {}).get("location", "")
            # Filter specifically for jobs mentioning 'India'
            if "India" in location or "Remote" in location: 
                jobs.append({
                    "title": job.get("text", "N/A"),
                    "company": "Zoho (via Lever)",
                    "location": location,
                    "description": "Various technical and non-technical roles. Filtered for India.",
                    "apply_link": job.get("hostedUrl", "N/A")
                })
        print(f"✅ Zoho (Lever): Found {len(jobs)} jobs.")
        return jobs
    except Exception as e:
        print("❌ Lever fetch failed:", e)
        return []

# === GREENHOUSE (Stripe Example) ===
def fetch_greenhouse_jobs():
    """Fetches jobs directly from the Greenhouse API for Stripe, filtering for India."""
    try:
        url = "https://boards-api.greenhouse.io/v1/boards/stripe/jobs"
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        data = r.json()
        
        jobs = []
        for job in data.get("jobs", []):
            location = job.get("location", {}).get("name", "")
            if "India" in location or "Remote" in location:
                jobs.append({
                    "title": job.get("title", "N/A"),
                    "company": "Stripe (via Greenhouse)",
                    "location": location,
                    "description": "Fintech and software roles for Stripe.",
                    "apply_link": job.get("absolute_url", "N/A")
                })
        print(f"✅ Stripe (Greenhouse): Found {len(jobs)} jobs.")
        return jobs
    except Exception as e:
        print("❌ Greenhouse fetch failed:", e)
        return []

# === WORKDAY (Accenture Example) - NOTE: Workday APIs are complex and often protected, but we try a public-facing URL ===
# This endpoint often requires complex session cookies and headers that simple 'requests' cannot provide, but we try the simplest GET.
def fetch_workday_jobs():
    """Fetches jobs from a public-facing Workday endpoint for Accenture (requires inspection)."""
    try:
        # NOTE: This endpoint often fails as it needs complex POST headers/session tokens. 
        # A simple GET request often only returns the JSON job list metadata, not the full job data.
        url = "https://accenture.wd3.myworkdayjobs.com/wday/cxs/accenture/Accenture_Careers/jobs"
        headers = {"Accept": "application/json"}
        r = requests.get(url, headers=headers, timeout=10)
        r.raise_for_status()
        data = r.json()
        
        jobs = []
        for job in data.get("jobPostings", []):
            location = job.get("locationsText", "")
            if "India" in location or "Remote" in location:
                # Construct the full application link from the external path
                apply_link = "https://accenture.wd3.myworkdayjobs.com/en-US/Accenture_Careers/job/" + job.get("externalPath", "")
                
                jobs.append({
                    "title": job.get("title", "N/A"),
                    "company": "Accenture (via Workday)",
                    "location": location,
                    "description": "Consulting and Technology roles in India.",
                    "apply_link": apply_link
                })
        print(f"✅ Accenture (Workday): Found {len(jobs)} jobs.")
        return jobs
    except Exception as e:
        print("❌ Workday fetch failed (Workday requires complex POST request):", e)
        return []


# --- 2. MAIN EXECUTION AND FORMATTING ---

def run_api_scraper():
    """Runs all fetch functions and formats the combined data for the index.html file."""
    ALL_JOBS = []
    
    # Collect data from all sources
    ALL_JOBS.extend(fetch_google_jobs())
    ALL_JOBS.extend(fetch_lever_jobs())
    ALL_JOBS.extend(fetch_greenhouse_jobs())
    ALL_JOBS.extend(fetch_workday_jobs())

    # Format into the final structure needed by index.html
    final_jobs_list = []
    today_date = datetime.now().strftime("%Y-%m-%d")
    
    for i, job in enumerate(ALL_JOBS):
        # Assign required fields for the index.html card structure
        final_jobs_list.append({
            "id": i + 1,
            "title": job.get("title", "Unknown Role"),
            "company": job.get("company", "External Source"),
            "location": job.get("location", "India"),
            "description": job.get("description", "Click the link to view full details and apply."),
            "link": job.get("apply_link", "#"),
            "postedDate": today_date # Crucial for the 30-day filter
        })
        
    return final_jobs_list

# === SAVE TO JSON ===
if __name__ == "__main__":
    real_job_data = run_api_scraper()

    # Save the data to a JSON file
    with open("real_jobs.json", "w", encoding="utf-8") as f:
        json.dump(real_job_data, f, indent=2, ensure_ascii=False)
        
    print(f"\n✅ COLLECTED {len(real_job_data)} JOBS ACROSS ALL SOURCES.")
    print("Data saved to real_jobs.json. Ready for copy-paste.")
    
    # Print the JSON content to the console for easy copy-paste
    print("\n\n--- COPY THIS SECTION INTO index.html ---")
    
    # Format the list of jobs for direct insertion into the JavaScript array
    jobs_js_format = ",\n".join([json.dumps(job, indent=4, ensure_ascii=False) for job in real_job_data])
    
    print("[\n" + jobs_js_format + "\n]")
    print("----------------------------------------\n")
