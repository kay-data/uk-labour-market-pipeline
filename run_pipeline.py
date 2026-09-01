import subprocess
import sys

steps = [
    ["src/ingestion/ons_api.py"],
    ["src/ingestion/ons_excel.py"],
    ["src/quality/validate_data.py"],
    ["src/transformation/spark_transform.py"],
    ["sql/sql_analysis.py"],
]

for step in steps:
    print(f"\nRunning: {step[0]}")
    subprocess.run([sys.executable, step[0]], check=True)

print("\nPipeline completed successfully.")