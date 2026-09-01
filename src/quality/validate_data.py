import pandas as pd
from pathlib import Path

def check_required_columns(df, required_columns):
    missing = [column for column in required_columns if column not in df.columns]

    if missing:
        print(f"Missing columns: {missing}")
        return False

    return True


def check_unique_periods(df):
    duplicates = df["period_date"].duplicated().sum()

    if duplicates:
        print(f"Duplicate periods: {duplicates}")
        return False

    return True


def check_unique_industry_periods(df):
    duplicates = df.duplicated(
        subset=["period", "industry"]
    ).sum()

    if duplicates:
        print(f"Duplicate period/industry combinations: {duplicates}")
        return False

    return True


def check_numeric_columns(df, columns):
    for column in columns:
        if not pd.api.types.is_numeric_dtype(df[column]):
            print(f"{column} is not numeric")
            return False

    return True


def check_missing_values(df, columns):
    missing = df[columns].isnull().sum()

    if missing.any():
        print(f"Missing values:\n{missing[missing > 0]}")
        return False

    return True


def check_non_negative(df, columns):
    for column in columns:
        if (df[column] < 0).any():
            print(f"{column} contains negative values")
            return False

    return True


if __name__ == "__main__":
    data_dir = Path("data/processed")

    vacs01 = pd.read_csv(data_dir / "vacs01.csv")
    vacs02 = pd.read_csv(data_dir / "vacs02.csv")

    vacs01_valid = (
        check_required_columns(
            vacs01,
            [
                "period_date",
                "period",
                "vacancies_thousands",
                "unemployment_thousands",
                "unemployed_per_vacancy",
            ],
        )
        and check_unique_periods(vacs01)
        and check_numeric_columns(
            vacs01,
            [
                "vacancies_thousands",
                "unemployment_thousands",
                "unemployed_per_vacancy",
            ],
        )
        and check_non_negative(
            vacs01,
            [
                "vacancies_thousands",
                "unemployment_thousands",
                "unemployed_per_vacancy",
            ],
        )
    )

    vacs02_valid = (
        check_required_columns(
            vacs02,
            [
                "period",
                "industry",
                "vacancies_thousands",
                "vacancies_per_100_jobs",
                "job_openings_rate",
                "period_date",
            ],
        )
        and check_unique_industry_periods(vacs02)
        and check_numeric_columns(
            vacs02,
            [
                "vacancies_thousands",
                "vacancies_per_100_jobs",
                "job_openings_rate",
            ],
        )
        and check_non_negative(
            vacs02,
            [
                "vacancies_thousands",
                "vacancies_per_100_jobs",
                "job_openings_rate",
            ],
        )
    )

    if vacs01_valid and vacs02_valid:
        print("All data quality checks passed.")

