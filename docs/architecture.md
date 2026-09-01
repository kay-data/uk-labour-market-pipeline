# Architecture

## Overview

This project is an end-to-end UK labour market data pipeline using official Office for National Statistics (ONS) vacancy and unemployment data.

The pipeline combines two ONS datasets:

- **VACS01 – Vacancies and Unemployment**, ingested through the ONS API.
- **VACS02 – Vacancies by industry**, downloaded as an Excel workbook and reshaped during transformation.

The purpose of the pipeline is to demonstrate a reproducible data-engineering workflow from source ingestion through validation, transformation, analytical modelling and querying.

## Data Flow

```text
ONS VACS01 API ───────────────┐
                              │
                              ▼
                        Raw ingestion
                              │
ONS VACS02 XLSX ──────────────┘
                              │
                              ▼
                         Validation
                              │
                              ▼
                      Data transformation
                              │
                              ▼
                           PySpark
                              │
                              ▼
                    Analytical data model
                         /          \
                        /            \
                       ▼              ▼
                     SQL           Power BI