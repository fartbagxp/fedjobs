"""Example usage of the Federal Jobs CLI programmatically."""

import os
from dotenv import load_dotenv
from fedjobs.main import USAJobsClient, display_jobs

# Load environment variables from .env file
load_dotenv()

api_key = os.getenv("USAJOBS_API_KEY")
email = os.getenv("USAJOBS_EMAIL")

if not api_key or not email:
    print("Please set USAJOBS_API_KEY and USAJOBS_EMAIL environment variables")
    exit(1)

# Initialize the client
client = USAJobsClient(api_key, email)

# Example 1: Search for IT Management positions (2210)
print("Example 1: IT Management positions (2210)")
print("=" * 50)
data = client.search_jobs(job_codes=["2210"], results_per_page=10)
display_jobs(data)

# Example 2: Search for CDC jobs
print("\n\nExample 2: CDC jobs")
print("=" * 50)
data = client.search_jobs(organization="CDC", results_per_page=10)
display_jobs(data)

# Example 3: Search for Computer Science (1550) and Data Science (1560) at CDC
print("\n\nExample 3: Computer Science and Data Science positions at CDC")
print("=" * 50)
data = client.search_jobs(
    job_codes=["1550", "1560"],
    organization="CDC",
    results_per_page=10
)
display_jobs(data, verbose=True)

# Example 4: Search with keyword
print("\n\nExample 4: Cybersecurity positions")
print("=" * 50)
data = client.search_jobs(
    job_codes=["2210"],
    keyword="cybersecurity",
    results_per_page=10
)
display_jobs(data)
