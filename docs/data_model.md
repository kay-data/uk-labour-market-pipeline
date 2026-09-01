# Data Model

## Purpose

The analytical model is designed to support analysis of UK vacancies, unemployment and vacancies by industry over time.

The model separates national labour-market measures from industry-level vacancy measures because the two datasets have different grains.

## Source Grains

### VACS01

**Grain:**

> One row represents one UK reporting period.

VACS01 contains national measures rather than industry-level observations.

Measures include:

- `vacancies_thousands`
- `unemployment_thousands`
- `unemployed_per_vacancy`

All measures are reported for the UK and are seasonally adjusted.

### VACS02

The ONS workbook contains industry-level vacancy data in a wide presentation format.

**Source structure:**

> One row represents one reporting period, with industry categories represented by columns.

For analytical use, the data is reshaped into long format.

**Analytical grain:**

> One row represents one reporting period and one industry.

This produces a fact structure in which industry is represented as a dimension rather than as a separate column for every industry.

## Dimensions

### dim_date

The date dimension represents the reporting period used by the ONS datasets.

Potential attributes include:

| Column | Description |
|---|---|
| `date_key` | Surrogate/date key |
| `period_start` | Start of the reporting period |
| `period_end` | End of the reporting period |
| `period_label` | Original ONS reporting-period label |
| `year` | Calendar year |
| `month` | Relevant calendar month |

The original ONS period label is retained because the source uses overlapping three-month reporting periods rather than simple calendar months.

### dim_industry

The industry dimension represents SIC 2007 industry classifications used by VACS02.

Potential attributes include:

| Column | Description |
|---|---|
| `industry_key` | Surrogate key |
| `industry_code` | SIC 2007 code |
| `industry_name` | Industry name |

The industry dimension allows the wide VACS02 source structure to be represented in a normalised analytical form.

## Fact Tables

### fact_national_labour_market

**Grain:**

> One row per UK reporting period.

Measures:

| Column | Description | Unit |
|---|---|---|
| `vacancies_thousands` | All vacancies | Thousands |
| `unemployment_thousands` | Unemployment | Thousands |
| `unemployed_per_vacancy` | Number of unemployed people per vacancy | Ratio |

Conceptually:

```text
fact_national_labour_market
--------------------------------
date_key
vacancies_thousands
unemployment_thousands
unemployed_per_vacancy