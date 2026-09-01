from pathlib import Path

import pandas as pd


def ingest_vacs02(file_path):
    file_path = Path(file_path)

    levels = pd.read_excel(
        file_path,
        sheet_name="levels",
        header=None,
    )

    ratios = pd.read_excel(
        file_path,
        sheet_name="ratios",
        header=None,
    )

    job_openings_rate = pd.read_excel(
        file_path,
        sheet_name="job openings rate",
        header=None,
    )

    return levels, ratios, job_openings_rate


def reshape_levels(df):
    industry_names = df.iloc[3, 2:].astype(str).str.strip()
    data = df.iloc[8:, :].copy()

    data = data.iloc[:, [0] + list(range(2, df.shape[1]))]

    data.columns = ["period"] + industry_names.tolist()

    data = data.melt(
        id_vars="period",
        var_name="industry",
        value_name="vacancies_thousands",
    )
    
    data = data[
        data["period"].str.match(
            r"^[A-Z][a-z]{2}-[A-Z][a-z]{2} \d{4}$",
            na=False,
        )
    ].copy()

    data["vacancies_thousands"] = pd.to_numeric(
        data["vacancies_thousands"],
        errors="coerce",
    )
    
    data = data[data["industry"] != "All vacancies1"].copy()

    return data


def reshape_ratios(df):
    industry_names = df.iloc[3, 2:].astype(str).str.strip()
    data = df.iloc[8:, :].copy()

    data = data.iloc[:, [0] + list(range(2, df.shape[1]))]

    data.columns = ["period"] + industry_names.tolist()

    data = data.melt(
        id_vars="period",
        var_name="industry",
        value_name="vacancies_per_100_jobs",
    )
    
    data = data[
        data["period"].str.match(
            r"^[A-Z][a-z]{2}-[A-Z][a-z]{2} \d{4}$",
            na=False,
        )
    ].copy()
    
    data["vacancies_per_100_jobs"] = pd.to_numeric(
        data["vacancies_per_100_jobs"],
        errors="coerce",
    )

    data = data[data["industry"] != "All vacancies2"].copy()

    return data


def reshape_job_openings_rate(df):
    industry_names = df.iloc[3, 2:].astype(str).str.strip()
    data = df.iloc[8:, :].copy()

    data = data.iloc[:, [0] + list(range(2, df.shape[1]))]

    data.columns = ["period"] + industry_names.tolist()

    data = data.melt(
        id_vars="period",
        var_name="industry",
        value_name="job_openings_rate",
    )
    
    data = data[
        data["period"].str.match(
            r"^[A-Z][a-z]{2}-[A-Z][a-z]{2} \d{4}$",
            na=False,
        )
    ].copy()

    data["job_openings_rate"] = pd.to_numeric(
        data["job_openings_rate"],
        errors="coerce",
    )

    data = data[data["industry"] != "All vacancies2"].copy()

    return data


def combine_vacs02(levels, ratios, job_openings_rate):
    df = levels.merge(
        ratios,
        on=["period", "industry"],
        how="outer",
    )

    df = df.merge(
        job_openings_rate,
        on=["period", "industry"],
        how="outer",
    )

    return df


def add_period_date(df):
    df = df.copy()

    start_month = df["period"].str[:3]
    year = df["period"].str[-4:]

    start_date = pd.to_datetime(
        start_month + " " + year,
        format="%b %Y",
    )

    df["period_date"] = start_date + pd.DateOffset(months=1)

    return df


if __name__ == "__main__":
    file_path = Path("data/raw/vacs02aug2026.xlsx")

    levels, ratios, job_openings_rate = ingest_vacs02(file_path)

    levels = reshape_levels(levels)
    ratios = reshape_ratios(ratios)
    job_openings_rate = reshape_job_openings_rate(job_openings_rate)

    df = combine_vacs02(
        levels,
        ratios,
        job_openings_rate,
    )

    df = add_period_date(df)

    print(df.head())
    print(df.shape)
    print(df.isnull().sum())