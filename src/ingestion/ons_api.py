from pathlib import Path

import pandas as pd
import requests


BASE_URL = "https://api.beta.ons.gov.uk/v1"


SERIES = {
    "AP2Y": "vacancies_thousands",
    "MGSC": "unemployment_thousands",
    "JPC5": "unemployed_per_vacancy",
}


def search_ons_series(cdid):
    url = f"{BASE_URL}/search"

    params = {
        "content_type": "timeseries",
        "q": cdid,
    }

    response = requests.get(url, params=params)
    response.raise_for_status()

    return response.json()


def fetch_ons_series(uri):
    url = f"{BASE_URL}/data"

    params = {
        "uri": uri,
    }

    response = requests.get(url, params=params)
    response.raise_for_status()

    return response.json()


def series_to_dataframe(data, measure_name):
    df = pd.DataFrame(data["months"])

    df = df[["date", "label", "value", "updateDate"]]

    df = df.rename(
        columns={
            "date": "period_date",
            "label": "period",
            "value": measure_name,
            "updateDate": "source_updated_at",
        }
    )

    df[measure_name] = pd.to_numeric(df[measure_name], errors="coerce")

    df["period_date"] = pd.to_datetime(
        df["period_date"],
        format="%Y %b"
    )

    df["source_updated_at"] = pd.to_datetime(
        df["source_updated_at"],
        utc=True
    )

    return df


def ingest_vacs01():
    series_data = []

    for cdid, measure_name in SERIES.items():
        search_results = search_ons_series(cdid)

        for item in search_results["items"]:
            if item["dataset_id"] == "LMS":
                data = fetch_ons_series(item["uri"])

                df = series_to_dataframe(
                    data,
                    measure_name,
                )

                series_data.append(df)
                break

    return series_data


def combine_vacs01(series_data):
    vacancies = series_data[0]
    unemployment = series_data[1]
    ratio = series_data[2]

    df = vacancies.merge(
        unemployment[["period_date", "unemployment_thousands"]],
        on="period_date",
        how="left",
    )

    df = df.merge(
        ratio[["period_date", "unemployed_per_vacancy"]],
        on="period_date",
        how="left",
    )

    return df


if __name__ == "__main__":
    series_data = ingest_vacs01()

    df = combine_vacs01(series_data)
    
    output_path = Path("data/processed/vacs01.csv")
    df.to_csv(output_path, index=False)

    print(f"Saved to {output_path}")

    print(df.head())
    print(df.dtypes)
    print(df.shape)
    print(df.isnull().sum())