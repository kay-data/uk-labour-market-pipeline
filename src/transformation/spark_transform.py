from pyspark.sql import SparkSession
from pyspark.sql.functions import col


def create_spark_session():
    return (
        SparkSession.builder
        .appName("UKLabourMarketPipeline")
        .config("spark.hadoop.fs.permissions.enabled", "false")
        .getOrCreate()
    )


def load_data(spark):
    vacs01 = (
        spark.read
        .option("header", True)
        .option("inferSchema", True)
        .csv("data/processed/vacs01.csv")
    )

    vacs02 = (
        spark.read
        .option("header", True)
        .option("inferSchema", True)
        .csv("data/processed/vacs02.csv")
    )

    return vacs01, vacs02


def transform_vacs01(df):
    return (
        df
        .withColumn("vacancies_thousands", col("vacancies_thousands").cast("double"))
        .withColumn("unemployment_thousands", col("unemployment_thousands").cast("double"))
        .withColumn("unemployed_per_vacancy", col("unemployed_per_vacancy").cast("double"))
    )


def transform_vacs02(df):
    return (
        df
        .withColumn("vacancies_thousands", col("vacancies_thousands").cast("double"))
        .withColumn("vacancies_per_100_jobs", col("vacancies_per_100_jobs").cast("double"))
        .withColumn("job_openings_rate", col("job_openings_rate").cast("double"))
    )
    
    
def save_as_parquet(vacs01, vacs02):
    vacs01.write.mode("overwrite").parquet(
        "data/output/fact_national_labour_market"
    )

    vacs02.write.mode("overwrite").parquet(
        "data/output/fact_industry_vacancies"
    )


if __name__ == "__main__":
    spark = create_spark_session()

    vacs01, vacs02 = load_data(spark)

    vacs01 = transform_vacs01(vacs01)
    vacs02 = transform_vacs02(vacs02)

    save_as_parquet(vacs01, vacs02)

    print("VACS01 rows:", vacs01.count())
    print("VACS02 rows:", vacs02.count())

    spark.stop()