from pyspark.sql import SparkSession


def create_spark_session():
    return (
        SparkSession.builder
        .appName("UKLabourMarketSQLAnalysis")
        .getOrCreate()
    )


def load_data(spark):
    national = spark.read.parquet(
        "data/output/fact_national_labour_market"
    )

    industry = spark.read.parquet(
        "data/output/fact_industry_vacancies"
    )

    national.createOrReplaceTempView("national_labour_market")
    industry.createOrReplaceTempView("industry_vacancies")


def run_analysis(spark):

    print("\n--- 1. Latest national labour market data ---")

    spark.sql("""
        SELECT
            period,
            vacancies_thousands,
            unemployment_thousands,
            unemployed_per_vacancy
        FROM national_labour_market
        ORDER BY period_date DESC
        LIMIT 10
    """).show(truncate=False)


    print("\n--- 2. Year-over-year vacancy change ---")

    spark.sql("""
        WITH vacancy_changes AS (
            SELECT
                period_date,
                period,
                vacancies_thousands,
                LAG(vacancies_thousands, 12) OVER (
                    ORDER BY period_date
                ) AS vacancies_previous_year
            FROM national_labour_market
        )
        SELECT
            period,
            vacancies_thousands,
            vacancies_previous_year,
            ROUND(
                vacancies_thousands - vacancies_previous_year,
                1
            ) AS vacancy_change
        FROM vacancy_changes
        WHERE vacancies_previous_year IS NOT NULL
        ORDER BY period_date DESC
        LIMIT 10
    """).show(truncate=False)


    print("\n--- 3. Industries with largest vacancy increases ---")

    spark.sql("""
        WITH industry_changes AS (
            SELECT
                period_date,
                period,
                industry,
                vacancies_thousands,
                LAG(vacancies_thousands) OVER (
                    PARTITION BY industry
                    ORDER BY period_date
                ) AS previous_vacancies
            FROM industry_vacancies
        )
        SELECT
            period,
            industry,
            vacancies_thousands,
            previous_vacancies,
            ROUND(
                vacancies_thousands - previous_vacancies,
                1
            ) AS vacancy_change
        FROM industry_changes
        WHERE previous_vacancies IS NOT NULL
        ORDER BY vacancy_change DESC
        LIMIT 10
    """).show(truncate=False)


    print("\n--- 4. Top industries by vacancy rate in latest period ---")

    spark.sql("""
        WITH latest_period AS (
            SELECT MAX(period_date) AS period_date
            FROM industry_vacancies
        ),
        ranked_industries AS (
            SELECT
                i.period,
                i.industry,
                i.vacancies_per_100_jobs,
                RANK() OVER (
                    ORDER BY i.vacancies_per_100_jobs DESC
                ) AS industry_rank
            FROM industry_vacancies i
            INNER JOIN latest_period l
                ON i.period_date = l.period_date
        )
        SELECT
            period,
            industry,
            vacancies_per_100_jobs,
            industry_rank
        FROM ranked_industries
        WHERE industry_rank <= 5
        ORDER BY industry_rank
    """).show(truncate=False)


    print("\n--- 5. Rolling unemployment-to-vacancy ratio ---")

    spark.sql("""
        SELECT
            period,
            unemployed_per_vacancy,
            ROUND(
                AVG(unemployed_per_vacancy) OVER (
                    ORDER BY period_date
                    ROWS BETWEEN 3 PRECEDING AND CURRENT ROW
                ),
                2
            ) AS rolling_4_period_average
        FROM national_labour_market
        ORDER BY period_date DESC
        LIMIT 10
    """).show(truncate=False)
    

if __name__ == "__main__":
    spark = create_spark_session()

    load_data(spark)
    run_analysis(spark)

    spark.stop()