# Fedjobs

A CLI tool for quick lookups of federal jobs from USAJOBS by job code and agency.

## Features

- Search jobs by occupational series codes (2210, 1550, 1560, etc.)
- Filter by federal agency (CDC, FDA, NASA, etc.)
- Search by keyword
- Beautiful formatted table output
- List common job codes and agencies

## Installation

1. Clone this repository:

```bash
git clone <your-repo-url>
cd fedjobs
```

2. Install dependencies using uv:

```bash
uv sync
```

Or with pip:

```bash
pip install -e .
```

## Setup

1. Get your API key from the [USAJOBS Developer Site](https://developer.usajobs.gov/apirequest/getapikey)

2. Set environment variables:

```bash
export USAJOBS_API_KEY="your_api_key_here"
export USAJOBS_EMAIL="your_email@example.com"
```

Or create a `.env` file (copy from `.env.example`):

```bash
cp .env.example .env
# Edit .env with your credentials
```

## Usage

### Search by Job Code

Search for IT Management positions (2210):

```bash
uv run python -m fedjobs.main search --job-code 2210
```

Search for multiple job codes:

```bash
uv run python -m fedjobs.main search --job-code 2210 --job-code 1550 --job-code 1560
```

### Search by Agency

Search for CDC jobs:

```bash
uv run python -m fedjobs.main search --agency CDC
```

### Combined Search

Search for IT positions at CDC:

```bash
uv run python -m fedjobs.main search --job-code 2210 --agency CDC
```

### Search with Keywords

Search for cybersecurity positions:

```bash
uv run python -m fedjobs.main search --job-code 2210 --keyword cybersecurity
```

### Additional Options

Show more results (up to 500):

```bash
uv run python -m fedjobs.main search --job-code 2210 --limit 50
```

Show verbose output with job codes and close dates:

```bash
uv run python -m fedjobs.main search --job-code 2210 --verbose
```

### Export Jobs to CSV

Export job search results to a CSV file with opening/closing dates and job URLs:

```bash
uv run python -m fedjobs.main export-csv --job-code 2210 --output active_jobs.csv
```

Append new results to an existing CSV file:

```bash
uv run python -m fedjobs.main export-csv --job-code 2210 --agency CDC --append
```

The CSV file includes:

- Position Title
- Agency
- Location
- Grade
- Salary Range
- Job Code
- Opening Date
- Closing Date
- Job URL (link to USAJOBS posting)

### List Available Codes and Agencies

List common job series codes:

```bash
uv run python -m fedjobs.main list-codes
```

List common federal agencies:

```bash
uv run python -m fedjobs.main list-agencies
```

## Common Job Series Codes

- **2210** - IT Management
- **1550** - Computer Science
- **1560** - Data Science

## Example Agencies

- **CDC** - Centers for Disease Control and Prevention
- **FDA** - Food and Drug Administration
- **NIH** - National Institutes of Health
- **NASA** - National Aeronautics and Space Administration

## Development

Run directly with Python:

```bash
uv run python -m fedjobs.main search --job-code 2210
```

## API Reference

This tool uses the [USAJOBS API](https://developer.usajobs.gov/tutorials/search-jobs) for job searches.

<!-- STATS_START -->

## Data Stats

> Last updated: **2026-07-17**

| Metric                            | Count      |
| --------------------------------- | ---------- |
| Total unique job postings tracked | **10,922** |
| Currently active positions        | **1,220**  |

### Active Positions by Job Series

| Series | Name                        | Active Postings |
| ------ | --------------------------- | --------------- |
| 0854   | Computer Engineering (0854) | 21              |
| 1550   | Computer Science (1550)     | 39              |
| 1560   | Data Science (1560)         | 20              |
| 2210   | IT Management (2210)        | 250             |

### Top Agencies (Active Postings)

| Agency                                   | Active Postings |
| ---------------------------------------- | --------------- |
| Veterans Health Administration           | 254             |
| Federal Aviation Administration          | 195             |
| Indian Health Service                    | 147             |
| Internal Revenue Service                 | 78              |
| Department of State - Agency Wide        | 42              |
| Social Security Administration           | 36              |
| Centers for Medicare & Medicaid Services | 28              |
| Air National Guard Units                 | 20              |
| National Institutes of Health            | 19              |
| Treasury, Departmental Offices           | 15              |

<!-- STATS_END -->
