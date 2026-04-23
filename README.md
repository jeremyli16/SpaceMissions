# Space Missions Dashboard

An interactive dashboard for exploring and analyzing historical space mission data from 1957 onwards, built with Python, Dash, and Plotly.

## Setup

**Requirements:** Python 3.14+

```bash
# Create and activate virtual environment
python -m venv .venv
.venv/Scripts/activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

Place `space_missions.csv` in the project root directory before running.

## Running

```bash
python main.py
```

Then open [http://127.0.0.1:8050](http://127.0.0.1:8050) in your browser.

## Features

### Dashboard
- **Summary stats**: total missions, overall success rate, and date range, all updated dynamically as filters change
- **Data table**: sortable and filterable table with pagination (20 rows/page)

### Filters
| Filter | Type | Description |
|---|---|---|
| Date Range | Date picker | Start and end date |
| Decade | Button group | Quickly restrict to a single decade (1950s–2020s) |
| Company | Multi-select dropdown | One or more organizations |
| Mission Status | Multi-select dropdown | Success, Failure, Partial Failure, Prelaunch Failure |
| Rocket Status | Multi-select dropdown | Active or Retired rockets |
| Country | Multi-select dropdown | Launch country, parsed from the Location field |
| Price Range | Slider | 0–5000 M$; missions with no price data always pass through |

A **Reset Filters** button restores all filters to their defaults.

### Visualizations
| Chart | Type | Rationale |
|---|---|---|
| Missions per Year | Line | Best for showing temporal trends — reveals the Space Race peak and post-Cold War decline |
| Top Companies by Mission Count | Horizontal bar | Ordered bars make ranking comparisons immediate; horizontal orientation fits long company names |
| Mission Status Breakdown | Donut | Part-of-whole relationship — shows overall success rate at a glance |
| Success Rate by Company | Horizontal bar | Compares quality vs. quantity across the top 10 organizations by volume (min. 5 missions) |

## Data Functions

The following functions are importable from `functions.py` independently of the dashboard:

```python
from functions import getMissionCountByCompany, getSuccessRate  # etc.
```

| Function | Returns | Notes |
|---|---|---|
| `getMissionCountByCompany(companyName: str)` | `int` | Returns `0` if company not found |
| `getSuccessRate(companyName: str)` | `float` | Rounded to 2 decimal places; returns `0.0` if company has no missions |
| `getMissionsByDateRange(startDate: str, endDate: str)` | `list[str]` | Mission names sorted chronologically; dates in `YYYY-MM-DD` format |
| `getTopCompaniesByMissionCount(n: int)` | `list[tuple]` | `[(name, count), ...]` sorted by count desc, then alphabetically |
| `getMissionStatusCount()` | `dict` | All 4 keys always present: `Success`, `Failure`, `Partial Failure`, `Prelaunch Failure` |
| `getMissionsByYear(year: int)` | `int` | Returns `0` if no missions in that year |
| `getMostUsedRocket()` | `str` | Alphabetical tiebreak; returns `""` if no data |
| `getAverageMissionsPerYear(startYear: int, endYear: int)` | `float` | Rounded to 2 decimal places; denominator is full year range, not just years with launches |

## Project Structure

```
SpaceMissions/
├── space_missions.csv   
├── functions.py         
├── app.py               
├── main.py              
├── assets/
│   └── custom.css       
└── requirements.txt
```
