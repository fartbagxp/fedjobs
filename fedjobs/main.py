"""Federal Jobs CLI - Quick lookup for USAJOBS postings."""

import csv
import os
import sys
from pathlib import Path
from typing import Optional

import click
import requests
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table
from rich import box

# Load environment variables from .env file
load_dotenv()

console = Console()

# Common job series codes
JOB_CODES = {
    "2210": "IT Management",
    "1550": "Computer Science",
    "1560": "Data Science",
}

# Common agency name to code mapping
# Maps user-friendly names to API agency codes
AGENCY_NAME_TO_CODE = {
    # Department of Health and Human Services
    "HHS": "HE",
    "HEALTH AND HUMAN SERVICES": "HE",
    "CDC": "HE39",
    "CENTERS FOR DISEASE CONTROL": "HE39",
    "FDA": "HE36",
    "FOOD AND DRUG ADMINISTRATION": "HE36",
    "NIH": "HE38",
    "NATIONAL INSTITUTES OF HEALTH": "HE38",
    "CMS": "HE70",
    "MEDICARE": "HE70",
    "IHS": "HE37",
    "INDIAN HEALTH SERVICE": "HE37",
    # NASA
    "NASA": "NN",
    "NATIONAL AERONAUTICS AND SPACE ADMINISTRATION": "NN",
    # USDA
    "USDA": "AG",
    "AGRICULTURE": "AG",
    "DEPARTMENT OF AGRICULTURE": "AG",
    # Other common agencies
    "DOD": "DD",
    "DEFENSE": "DD",
    "DEPARTMENT OF DEFENSE": "DD",
    "VA": "VA",
    "VETERANS AFFAIRS": "VA",
    "DHS": "HS",
    "HOMELAND SECURITY": "HS",
    "DOJ": "DJ",
    "JUSTICE": "DJ",
    "DEPARTMENT OF JUSTICE": "DJ",
    "STATE": "ST",
    "DEPARTMENT OF STATE": "ST",
    "TREASURY": "TR",
    "DEPARTMENT OF TREASURY": "TR",
    "DOE": "EN",
    "ENERGY": "EN",
    "DEPARTMENT OF ENERGY": "EN",
    "DOI": "IN",
    "INTERIOR": "IN",
    "DEPARTMENT OF INTERIOR": "IN",
}

# Path to agency codes CSV
DATA_DIR = Path(__file__).parent.parent / "data" / "raw"
AGENCIES_CSV = DATA_DIR / "agency_codes.csv"


class USAJobsClient:
    """Client for interacting with the USAJOBS API."""

    BASE_URL = "https://data.usajobs.gov/api/search"

    def __init__(self, api_key: str, email: str):
        """Initialize the client with API credentials.

        Args:
            api_key: USAJOBS API key
            email: Your email address for User-Agent header
        """
        self.api_key = api_key
        self.email = email

    def search_jobs(
        self,
        job_codes: Optional[list[str]] = None,
        organization: Optional[str] = None,
        keyword: Optional[str] = None,
        results_per_page: int = 25,
    ) -> dict:
        """Search for federal jobs.

        Args:
            job_codes: List of occupational series codes (e.g., ["2210", "1550"])
            organization: Organization/agency name (e.g., "CDC")
            keyword: Search keyword
            results_per_page: Number of results to return (max 500)

        Returns:
            API response as dictionary
        """
        headers = {
            "Host": "data.usajobs.gov",
            "User-Agent": self.email,
            "Authorization-Key": self.api_key,
        }

        params = {}

        if job_codes:
            params["JobCategoryCode"] = ";".join(job_codes)

        if organization:
            params["Organization"] = organization

        if keyword:
            params["Keyword"] = keyword

        params["ResultsPerPage"] = results_per_page

        try:
            response = requests.get(self.BASE_URL, headers=headers, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            console.print(f"[red]Error calling USAJOBS API: {e}[/red]")
            sys.exit(1)


def fetch_agency_codes() -> list[dict]:
    """Fetch agency codes from USAJOBS API.

    Returns:
        List of agency dictionaries with code, name, acronym, etc.
    """
    url = "https://data.usajobs.gov/api/codelist/agencysubelements"

    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        data = response.json()

        # Extract the ValidValue list from the nested structure
        agencies = data.get("CodeList", [{}])[0].get("ValidValue", [])
        return agencies
    except requests.exceptions.RequestException as e:
        console.print(f"[red]Error fetching agency codes: {e}[/red]")
        return []


def save_agency_codes_to_csv(agencies: list[dict], filepath: Path) -> None:
    """Save agency codes to a CSV file.

    Args:
        agencies: List of agency dictionaries from API
        filepath: Path to save the CSV file
    """
    # Ensure directory exists
    filepath.parent.mkdir(parents=True, exist_ok=True)

    # Filter out disabled agencies
    active_agencies = [a for a in agencies if a.get("IsDisabled") != "Yes"]

    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["Code", "Value", "ParentCode", "Acronym", "LastModified"],
            extrasaction="ignore",
        )
        writer.writeheader()
        writer.writerows(active_agencies)

    console.print(
        f"[green]Saved {len(active_agencies)} agency codes to {filepath}[/green]"
    )


def update_agency_codes() -> None:
    """Fetch and save the latest agency codes from USAJOBS API."""
    console.print("[bold]Fetching agency codes from USAJOBS API...[/bold]")
    agencies = fetch_agency_codes()

    if agencies:
        save_agency_codes_to_csv(agencies, AGENCIES_CSV)
    else:
        console.print("[red]Failed to fetch agency codes[/red]")


def translate_agency_name(agency: str) -> str:
    """Translate a user-friendly agency name to its API code.

    Args:
        agency: User-provided agency name or code

    Returns:
        API agency code (returns input if already a valid code or no mapping found)
    """
    # Check if it's already in our mapping
    upper_agency = agency.upper()
    if upper_agency in AGENCY_NAME_TO_CODE:
        return AGENCY_NAME_TO_CODE[upper_agency]

    # Otherwise, assume it's already a code and return as-is
    return agency


def display_jobs(data: dict, verbose: bool = False):
    """Display job search results in a formatted table.

    Args:
        data: API response data
        verbose: Show additional details
    """
    search_result = data.get("SearchResult", {})
    count = search_result.get("SearchResultCount", 0)
    total_count = search_result.get("SearchResultCountAll", 0)
    items = search_result.get("SearchResultItems", [])

    console.print(
        f"\n[bold green]Found {count} jobs (Total: {total_count})[/bold green]\n"
    )

    if not items:
        console.print("[yellow]No jobs found matching your criteria.[/yellow]")
        return

    table = Table(show_header=True, header_style="bold cyan", box=box.ROUNDED)
    table.add_column("Position", style="bold")
    table.add_column("Agency", max_width=30)
    table.add_column("Location", max_width=25)
    table.add_column("Grade", justify="center")
    table.add_column("Salary", justify="right")

    if verbose:
        table.add_column("Job Code", justify="center")
        table.add_column("Close Date", justify="center")

    for item in items:
        job = item.get("MatchedObjectDescriptor", {})

        position_title = job.get("PositionTitle", "N/A")
        organization = job.get("OrganizationName", "N/A")

        # Handle locations
        locations = job.get("PositionLocation", [])
        if locations:
            location_name = locations[0].get("LocationName", "N/A")
        else:
            location_name = "N/A"

        # Grade information
        grade_info = job.get("JobGrade", [{}])[0] if job.get("JobGrade") else {}
        grade = grade_info.get("Code", "N/A")

        # Salary range
        salary_min = job.get("PositionRemuneration", [{}])[0].get("MinimumRange", "N/A")
        salary_max = job.get("PositionRemuneration", [{}])[0].get("MaximumRange", "N/A")
        salary = f"${salary_min}-{salary_max}" if salary_min != "N/A" else "N/A"

        row = [position_title, organization, location_name, grade, salary]

        if verbose:
            job_codes = job.get("JobCategory", [])
            job_code = job_codes[0].get("Code", "N/A") if job_codes else "N/A"
            close_date = (
                job.get("ApplicationCloseDate", "N/A")[:10]
                if job.get("ApplicationCloseDate")
                else "N/A"
            )
            row.extend([job_code, close_date])

        table.add_row(*row)

    console.print(table)


@click.group()
def cli():
    """Federal Jobs CLI - Quick lookup for USAJOBS postings."""
    pass


@cli.command()
@click.option(
    "--job-code",
    "-j",
    multiple=True,
    help="Job series code (e.g., 2210, 1550). Can specify multiple times.",
)
@click.option(
    "--agency",
    "-a",
    help="Agency name (e.g., CDC, FDA, NASA)",
)
@click.option(
    "--keyword",
    "-k",
    help="Search keyword",
)
@click.option(
    "--limit",
    "-l",
    default=25,
    type=int,
    help="Number of results to return (max 500)",
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Show additional job details",
)
def search(job_code, agency, keyword, limit, verbose):
    """Search for federal jobs by job code and/or agency."""
    api_key = os.getenv("USAJOBS_API_KEY")
    email = os.getenv("USAJOBS_EMAIL")

    if not api_key or not email:
        console.print(
            "[red]Error: USAJOBS_API_KEY and USAJOBS_EMAIL environment variables required.[/red]\n"
            "Get your API key at: https://developer.usajobs.gov/apirequest/getapikey"
        )
        sys.exit(1)

    if not job_code and not agency and not keyword:
        console.print(
            "[yellow]Please specify at least one filter: --job-code, --agency, or --keyword[/yellow]"
        )
        sys.exit(1)

    client = USAJobsClient(api_key, email)

    # Translate agency name to code if needed
    agency_code = None
    if agency:
        agency_code = translate_agency_name(agency)

    search_params = []
    if job_code:
        codes = ", ".join(job_code)
        search_params.append(f"Job Codes: {codes}")
    if agency:
        if agency_code != agency:
            search_params.append(f"Agency: {agency} (code: {agency_code})")
        else:
            search_params.append(f"Agency: {agency}")
    if keyword:
        search_params.append(f"Keyword: {keyword}")

    console.print(f"[bold]Searching for jobs:[/bold] {' | '.join(search_params)}\n")

    data = client.search_jobs(
        job_codes=list(job_code) if job_code else None,
        organization=agency_code,
        keyword=keyword,
        results_per_page=limit,
    )

    display_jobs(data, verbose=verbose)


@cli.command()
def list_codes():
    """List common job series codes."""
    table = Table(
        title="Common Job Series Codes", show_header=True, header_style="bold cyan"
    )
    table.add_column("Code", style="bold", justify="center")
    table.add_column("Title")

    for code, title in JOB_CODES.items():
        table.add_row(code, title)

    console.print(table)


@cli.command()
@click.option(
    "--all",
    "-a",
    "show_all",
    is_flag=True,
    help="Show all agencies from CSV file instead of just common ones",
)
def list_agencies(show_all):
    """List federal agencies and their codes."""
    if show_all and AGENCIES_CSV.exists():
        # Read from CSV and display all agencies
        table = Table(
            title="All Federal Agencies",
            show_header=True,
            header_style="bold cyan",
            box=box.ROUNDED,
        )
        table.add_column("Code", style="bold", justify="center")
        table.add_column("Agency Name", max_width=60)
        table.add_column("Acronym", justify="center")

        with open(AGENCIES_CSV, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                table.add_row(
                    row.get("Code", ""), row.get("Value", ""), row.get("Acronym", "")
                )

        console.print(table)
        console.print(f"\n[dim]Total agencies: {table.row_count}[/dim]")
    else:
        if show_all and not AGENCIES_CSV.exists():
            console.print(
                "[yellow]Agency CSV not found. Run 'fedjobs update-agencies' first.[/yellow]\n"
            )

        # Show common agency mappings
        table = Table(
            title="Common Federal Agencies",
            show_header=True,
            header_style="bold cyan",
            box=box.ROUNDED,
        )
        table.add_column("Name/Abbreviation", style="bold")
        table.add_column("API Code", justify="center")

        # Group by code to avoid duplicates
        code_to_names = {}
        for name, code in sorted(AGENCY_NAME_TO_CODE.items()):
            if code not in code_to_names:
                code_to_names[code] = []
            code_to_names[code].append(name)

        # Display unique codes with their primary name
        seen_codes = set()
        for name, code in sorted(AGENCY_NAME_TO_CODE.items()):
            if code not in seen_codes:
                table.add_row(name, code)
                seen_codes.add(code)

        console.print(table)
        console.print("\n[dim]Tip: Use --all to see all available agencies[/dim]")


@cli.command()
def update_agencies():
    """Fetch and update the agency codes CSV from USAJOBS API."""
    update_agency_codes()


@cli.command()
@click.option(
    "--job-code",
    "-j",
    multiple=True,
    help="Job series code (e.g., 2210, 1550). Can specify multiple times.",
)
@click.option(
    "--agency",
    "-a",
    help="Agency name (e.g., CDC, FDA, NASA)",
)
@click.option(
    "--keyword",
    "-k",
    help="Search keyword",
)
@click.option(
    "--limit",
    "-l",
    default=25,
    type=int,
    help="Number of results to return (max 500)",
)
@click.option(
    "--output",
    "-o",
    default="active_jobs.csv",
    type=click.Path(),
    help="Output CSV file path (default: active_jobs.csv)",
)
@click.option(
    "--append",
    is_flag=True,
    help="Append to existing CSV file instead of overwriting",
)
def export_csv(job_code, agency, keyword, limit, output, append):
    """Export job search results to a CSV file with opening/closing dates and job URLs."""
    api_key = os.getenv("USAJOBS_API_KEY")
    email = os.getenv("USAJOBS_EMAIL")

    if not api_key or not email:
        console.print(
            "[red]Error: USAJOBS_API_KEY and USAJOBS_EMAIL environment variables required.[/red]\n"
            "Get your API key at: https://developer.usajobs.gov/apirequest/getapikey"
        )
        sys.exit(1)

    if not job_code and not agency and not keyword:
        console.print(
            "[yellow]Please specify at least one filter: --job-code, --agency, or --keyword[/yellow]"
        )
        sys.exit(1)

    client = USAJobsClient(api_key, email)

    # Translate agency name to code if needed
    agency_code = None
    if agency:
        agency_code = translate_agency_name(agency)

    search_params = []
    if job_code:
        codes = ", ".join(job_code)
        search_params.append(f"Job Codes: {codes}")
    if agency:
        if agency_code != agency:
            search_params.append(f"Agency: {agency} (code: {agency_code})")
        else:
            search_params.append(f"Agency: {agency}")
    if keyword:
        search_params.append(f"Keyword: {keyword}")

    console.print(f"[bold]Searching for jobs:[/bold] {' | '.join(search_params)}\n")

    data = client.search_jobs(
        job_codes=list(job_code) if job_code else None,
        organization=agency_code,
        keyword=keyword,
        results_per_page=limit,
    )

    search_result = data.get("SearchResult", {})
    count = search_result.get("SearchResultCount", 0)
    items = search_result.get("SearchResultItems", [])

    if not items:
        console.print("[yellow]No jobs found matching your criteria.[/yellow]")
        return

    console.print(f"[bold green]Found {count} jobs[/bold green]")

    # Prepare CSV data
    output_path = Path(output)
    file_exists = output_path.exists()

    # Determine write mode
    mode = "a" if (append and file_exists) else "w"

    with open(output_path, mode, newline="", encoding="utf-8") as csvfile:
        fieldnames = [
            "Position Title",
            "Agency",
            "Location",
            "Grade",
            "Salary Min",
            "Salary Max",
            "Job Code",
            "Opening Date",
            "Closing Date",
            "Job URL",
        ]

        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        # Write header only if file is new or we're overwriting
        if mode == "w" or not file_exists:
            writer.writeheader()

        # Collect job data
        rows = []
        for item in items:
            job = item.get("MatchedObjectDescriptor", {})

            # Extract job details
            position_title = job.get("PositionTitle", "")
            organization = job.get("OrganizationName", "")

            # Handle locations
            locations = job.get("PositionLocation", [])
            location_name = locations[0].get("LocationName", "") if locations else ""

            # Grade information
            grade_info = job.get("JobGrade", [{}])[0] if job.get("JobGrade") else {}
            grade = grade_info.get("Code", "")

            # Salary range
            salary_info = (
                job.get("PositionRemuneration", [{}])[0]
                if job.get("PositionRemuneration")
                else {}
            )
            salary_min = salary_info.get("MinimumRange", "")
            salary_max = salary_info.get("MaximumRange", "")

            # Job codes
            job_codes = job.get("JobCategory", [])
            job_code_str = job_codes[0].get("Code", "") if job_codes else ""

            # Dates
            opening_date = job.get(
                "PublicationStartDate", job.get("PositionStartDate", "")
            )
            if opening_date:
                opening_date = opening_date[:10]  # Extract just the date part

            closing_date = job.get("ApplicationCloseDate", "")
            if closing_date:
                closing_date = closing_date[:10]  # Extract just the date part

            # Job URL
            job_url = job.get("PositionURI", "")

            rows.append(
                {
                    "Position Title": position_title,
                    "Agency": organization,
                    "Location": location_name,
                    "Grade": grade,
                    "Salary Min": salary_min,
                    "Salary Max": salary_max,
                    "Job Code": job_code_str,
                    "Opening Date": opening_date,
                    "Closing Date": closing_date,
                    "Job URL": job_url,
                }
            )

        # Sort by Agency, then Position Title, then Location, then Grade
        rows.sort(key=lambda r: (r["Agency"], r["Position Title"], r["Location"], r["Grade"]))

        writer.writerows(rows)

    action = "Appended" if (append and file_exists) else "Exported"
    console.print(f"\n[bold green]{action} {count} jobs to {output_path}[/bold green]")


if __name__ == "__main__":
    cli()
