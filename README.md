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
- **Summary stats** — total missions, overall success rate, and date range, all updated dynamically as filters change
- **Interactive filters** — date range picker, multi-select company dropdown, and mission status filter with a reset button to restore defaults
- **Data table** — sortable and filterable table with pagination (20 rows/page)

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

| Function | Returns |
|---|---|
| `getMissionCountByCompany(companyName: str)` | `int` |
| `getSuccessRate(companyName: str)` | `float` — % rounded to 2 decimal places |
| `getMissionsByDateRange(startDate: str, endDate: str)` | `list[str]` — mission names sorted chronologically |
| `getTopCompaniesByMissionCount(n: int)` | `list[tuple]` — `[(name, count), ...]` |
| `getMissionStatusCount()` | `dict` — counts for all 4 statuses |
| `getMissionsByYear(year: int)` | `int` |
| `getMostUsedRocket()` | `str` |
| `getAverageMissionsPerYear(startYear: int, endYear: int)` | `float` — rounded to 2 decimal places |

## Project Structure

```
SpaceMissions/
├── space_missions.csv   # data file (not committed)
├── functions.py         # data functions (no Dash imports — safe to import standalone)
├── app.py               # Dash layout and callbacks
├── main.py              # entry point
├── assets/
│   └── custom.css       # date picker styling overrides
└── requirements.txt
```
