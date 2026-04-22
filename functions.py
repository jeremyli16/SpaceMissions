import sys
from pathlib import Path

import pandas as pd

CSV_PATH = Path(__file__).parent / "space_missions.csv"

DATA_LOADED = False
_COLUMNS = ["Company", "Location", "Date", "Time", "Rocket", "Mission", "RocketStatus", "Price", "MissionStatus"]

try:
    df = pd.read_csv(CSV_PATH)
    for col in ["Company", "MissionStatus", "Rocket", "Mission"]:
        if col in df.columns:
            df[col] = df[col].str.strip()
    df["Date"] = pd.to_datetime(df["Date"], format="%Y-%m-%d", errors="coerce")
    if "Price" in df.columns:
        df["Price"] = (
            df["Price"].astype(str).str.replace(",", "", regex=False)
            .replace("nan", pd.NA)
        )
        df["Price"] = pd.to_numeric(df["Price"], errors="coerce")
    DATA_LOADED = True
except FileNotFoundError:
    print(f"WARNING: space_missions.csv not found at {CSV_PATH}. All functions will return empty/zero values.", file=sys.stderr)
    df = pd.DataFrame(columns=_COLUMNS)
except pd.errors.EmptyDataError:
    print(f"WARNING: space_missions.csv is empty at {CSV_PATH}.", file=sys.stderr)
    df = pd.DataFrame(columns=_COLUMNS)


def getMissionCountByCompany(companyName: str) -> int:
    if df.empty:
        return 0
    return int((df["Company"] == companyName).sum())


def getSuccessRate(companyName: str) -> float:
    if df.empty:
        return 0.0
    company_df = df[df["Company"] == companyName]
    total = len(company_df)
    if total == 0:
        return 0.0
    successes = int((company_df["MissionStatus"] == "Success").sum())
    return round((successes / total) * 100, 2)


def getMissionsByDateRange(startDate: str, endDate: str) -> list:
    if df.empty:
        return []
    try:
        start = pd.to_datetime(startDate, format="%Y-%m-%d")
        end = pd.to_datetime(endDate, format="%Y-%m-%d")
    except (ValueError, TypeError):
        return []
    mask = (df["Date"] >= start) & (df["Date"] <= end)
    result = df.loc[mask].sort_values("Date")["Mission"].tolist()
    return result


def getTopCompaniesByMissionCount(n: int) -> list:
    if df.empty or n <= 0:
        return []
    counts = df.groupby("Company", dropna=True).size().reset_index(name="count")
    counts = counts.sort_values(["count", "Company"], ascending=[False, True])
    top = counts.head(n)
    return [(row["Company"], int(row["count"])) for _, row in top.iterrows()]


def getMissionStatusCount() -> dict:
    result = {"Success": 0, "Failure": 0, "Partial Failure": 0, "Prelaunch Failure": 0}
    if df.empty:
        return result
    counts = df["MissionStatus"].value_counts()
    for key in result:
        if key in counts.index:
            result[key] = int(counts[key])
    return result


def getMissionsByYear(year: int) -> int:
    if df.empty:
        return 0
    return int((df["Date"].dt.year == year).sum())


def getMostUsedRocket() -> str:
    if df.empty:
        return ""
    counts = df.groupby("Rocket", dropna=True).size()
    max_count = counts.max()
    tied = sorted(counts[counts == max_count].index.tolist())
    return tied[0]


def getAverageMissionsPerYear(startYear: int, endYear: int) -> float:
    if startYear > endYear:
        return 0.0
    if df.empty:
        return 0.0
    mask = (df["Date"].dt.year >= startYear) & (df["Date"].dt.year <= endYear)
    total_missions = int(mask.sum())
    num_years = endYear - startYear + 1
    return round(total_missions / num_years, 2)
