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
fedjobs search --job-code 2210
```

Search for multiple job codes:

```bash
fedjobs search --job-code 2210 --job-code 1550 --job-code 1560
```

### Search by Agency

Search for CDC jobs:

```bash
fedjobs search --agency CDC
```

### Combined Search

Search for IT positions at CDC:

```bash
fedjobs search --job-code 2210 --agency CDC
```

### Search with Keywords

Search for cybersecurity positions:

```bash
fedjobs search --job-code 2210 --keyword cybersecurity
```

### Additional Options

Show more results (up to 500):

```bash
fedjobs search --job-code 2210 --limit 50
```

Show verbose output with job codes and close dates:

```bash
fedjobs search --job-code 2210 --verbose
```

### List Available Codes and Agencies

List common job series codes:

```bash
fedjobs list-codes
```

List common federal agencies:

```bash
fedjobs list-agencies
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
