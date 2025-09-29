import requests

# -------- LEVER API -------- #
def fetch_lever_jobs(company):
    url = f"https://api.lever.co/v0/postings/{company}?mode=json"
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        jobs = []
        for job in r.json():
            jobs.append({
                "company": company.capitalize(),
                "title": job.get("text", "No title"),
                "location": job["categories"].get("location", "Not specified"),
                "team": job["categories"].get("team", ""),
                "apply_link": job.get("hostedUrl", "#")
            })
        return jobs
    except Exception as e:
        print(f"[Lever] Error fetching {company}: {e}")
        return []

# -------- GREENHOUSE API -------- #
def fetch_greenhouse_jobs(company_id, company_name):
    url = f"https://boards-api.greenhouse.io/v1/boards/{company_id}/jobs"
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        jobs = []
        for job in r.json().get("jobs", []):
            jobs.append({
                "company": company_name,
                "title": job.get("title", "No title"),
                "location": job.get("location", {}).get("name", "Not specified"),
                "apply_link": job.get("absolute_url", "#")
            })
        return jobs
    except Exception as e:
        print(f"[Greenhouse] Error fetching {company_name}: {e}")
        return []

# -------- MAIN -------- #
if __name__ == "__main__":
    all_jobs = []

    # Lever-based MNCs
    lever_companies = ["stripe", "netflix", "shopify", "dropbox", "robinhood"]
    for company in lever_companies:
        all_jobs.extend(fetch_lever_jobs(company))

    # Greenhouse-based MNCs
    greenhouse_companies = {
        "coinbase": "Coinbase",
        "twilio": "Twilio",
        "datadog": "Datadog",
        "palantir": "Palantir",
        "airbnb": "Airbnb"
    }
    for cid, cname in greenhouse_companies.items():
        all_jobs.extend(fetch_greenhouse_jobs(cid, cname))

    # ✅ Print collected jobs
    for job in all_jobs[:20]:  # limit preview
        print(f"{job['company']} - {job['title']} ({job['location']})")
        print(f"Apply: {job['apply_link']}\n")

    print(f"Total jobs collected: {len(all_jobs)}")
