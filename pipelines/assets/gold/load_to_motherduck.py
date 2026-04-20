""" @bruin
name: gold.load_to_motherduck
type: python
depends:
    - silver.data_normalization
description: "Upload and create table for dashboard."
@bruin """

import os
import duckdb
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

R2_ACCESS_KEY = os.getenv("R2_ACCESS_KEY")
R2_SECRET_KEY = os.getenv("R2_SECRET_KEY")
R2_ENDPOINT = f"{os.getenv('R2_ACCOUNT_ID')}.r2.cloudflarestorage.com"
MOTHERDUCK_TOKEN = os.getenv("MOTHERDUCK_TOKEN")

def setup_connection():
    con = duckdb.connect(f"md:?motherduck_token={MOTHERDUCK_TOKEN}")
    con.execute("INSTALL httpfs; LOAD httpfs;")
    con.execute(f"""
        CREATE OR REPLACE SECRET r2_secret (
            TYPE S3,
            KEY_ID '{R2_ACCESS_KEY}',
            SECRET '{R2_SECRET_KEY}',
            ENDPOINT '{R2_ENDPOINT}',
            REGION 'auto',
            URL_STYLE 'path'
        );
    """)
    return con

def create_tables(con):
    # Create database and load it to staging_raw table
    con.execute("CREATE DATABASE IF NOT EXISTS scm_db;")
    con.execute("USE scm_db;")
    con.execute("""
    CREATE OR REPLACE TABLE staging_raw AS
    SELECT * FROM read_parquet(
        's3://scm-car-dataset/silver/part-00000-53643c17-b36c-4b24-a8fa-09754f1e8bc4-c000.snappy.parquet'
        );
    """)
    
def create_dimensions(con):
    # Dim Customer
    con.execute("""
        CREATE OR REPLACE TABLE dim_customer AS
        SELECT DISTINCT
            CustomerID,
            CustomerName,
            Gender,
            JobTitle,
            CASE
                -- Engineering
                WHEN JobTitle ILIKE '%Engineer%' THEN 'Engineering'

                -- IT & Software
                WHEN JobTitle ILIKE '%Developer%'
                OR JobTitle ILIKE '%Programmer%'
                OR JobTitle ILIKE '%Software%'
                OR JobTitle ILIKE '%Systems Administrator%'
                OR JobTitle ILIKE '%Database Administrator%'
                OR JobTitle ILIKE '%Web Developer%'
                OR JobTitle ILIKE '%Web Designer%'
                OR JobTitle ILIKE '%IT%'
                THEN 'IT & Software'

                -- Data & Analytics
                WHEN JobTitle ILIKE '%Analyst%'
                OR JobTitle ILIKE '%Statistician%'
                OR JobTitle ILIKE '%Biostatistician%'
                OR JobTitle ILIKE '%Actuary%'
                THEN 'Data & Analytics'

                -- Finance
                WHEN JobTitle ILIKE '%Accountant%'
                OR JobTitle ILIKE '%Financial%'
                OR JobTitle ILIKE '%Accounting%'
                OR JobTitle ILIKE '%Auditor%'
                OR JobTitle ILIKE '%Cost%'
                THEN 'Finance & Accounting'

                -- Sales & Marketing
                WHEN JobTitle ILIKE '%Sales%'
                OR JobTitle ILIKE '%Marketing%'
                OR JobTitle ILIKE '%Account Executive%'
                OR JobTitle ILIKE '%Sales Associate%'
                THEN 'Sales & Marketing'

                -- HR & Admin
                WHEN JobTitle ILIKE '%Human Resources%'
                OR JobTitle ILIKE '%Recruit%'
                OR JobTitle ILIKE '%Administrative%'
                OR JobTitle ILIKE '%Office Assistant%'
                OR JobTitle ILIKE '%Secretary%'
                THEN 'HR & Admin'

                -- Healthcare
                WHEN JobTitle ILIKE '%Nurse%'
                OR JobTitle ILIKE '%Therapist%'
                OR JobTitle ILIKE '%Pharmacist%'
                OR JobTitle ILIKE '%Dental%'
                OR JobTitle ILIKE '%Clinical%'
                THEN 'Healthcare'

                -- Education
                WHEN JobTitle ILIKE '%Professor%'
                OR JobTitle ILIKE '%Teacher%'
                OR JobTitle ILIKE '%Research%'
                THEN 'Education & Research'

                -- Legal
                WHEN JobTitle ILIKE '%Legal%'
                OR JobTitle ILIKE '%Paralegal%'
                THEN 'Legal'

                -- Creative
                WHEN JobTitle ILIKE '%Designer%'
                OR JobTitle ILIKE '%Media%'
                OR JobTitle ILIKE '%Editor%'
                OR JobTitle ILIKE '%Writer%'
                THEN 'Creative & Media'

                -- Operations
                WHEN JobTitle ILIKE '%Manager%'
                OR JobTitle ILIKE '%Operator%'
                OR JobTitle ILIKE '%Coordinator%'
                THEN 'Operations'

                ELSE 'Others'
            END AS job_group,
            PhoneNumber,
            EmailAddress,
            CustomerAddress,
            City,
            State,
            Country,
            CountryCode,
            PostalCode,
            ProductID,
            SupplierID
        FROM staging_raw;
    """)
    
    # Dim Product
    con.execute("""
        CREATE OR REPLACE TABLE dim_product AS
        SELECT DISTINCT
            ProductID,
            CarMaker,
            CarModel,
            CASE
                WHEN CarModel ILIKE '%Truck%' 
                OR CarModel ILIKE '%F150%'
                OR CarModel ILIKE '%F250%'
                OR CarModel ILIKE '%Ram%'
                OR CarModel ILIKE '%Silverado%'
                THEN 'Truck'

                WHEN CarModel ILIKE '%SUV%'
                OR CarModel ILIKE '%Explorer%'
                OR CarModel ILIKE '%Highlander%'
                OR CarModel ILIKE '%RAV4%'
                OR CarModel ILIKE '%CR-V%'
                OR CarModel ILIKE '%Range Rover%'
                THEN 'SUV'

                WHEN CarModel ILIKE '%Coupe%'
                OR CarModel ILIKE '%Mustang%'
                OR CarModel ILIKE '%Camaro%'
                THEN 'Coupe'

                WHEN CarModel ILIKE '%Civic%'
                OR CarModel ILIKE '%Corolla%'
                OR CarModel ILIKE '%Accord%'
                OR CarModel ILIKE '%Camry%'
                THEN 'Sedan'

                WHEN CarModel ILIKE '%Van%'
                OR CarModel ILIKE '%Econoline%'
                OR CarModel ILIKE '%Express%'
                THEN 'Van'

                WHEN CarModel ILIKE '%Ferrari%'
                OR CarModel ILIKE '%Lamborghini%'
                OR CarModel ILIKE '%Bentley%'
                THEN 'Luxury'

                ELSE 'Others'
            END AS car_type,
            CarColor,
            CASE
                WHEN CarColor IN ('Red', 'Crimson', 'Maroon', 'Pink', 'Fuchsia') THEN 'Red & Pink'
                WHEN CarColor IN ('Purple', 'Violet', 'Indigo', 'Mauve', 'Puce') THEN 'Purple'
                WHEN CarColor IN ('Blue', 'Teal', 'Turquoise', 'Aquamarine') THEN 'Blue & Teal'
                WHEN CarColor = 'Green' THEN 'Green'
                WHEN CarColor IN ('Yellow', 'Orange', 'Goldenrod') THEN 'Yellow & Orange'
                WHEN CarColor = 'Khaki' THEN 'Earth Tones'
                
                ELSE 'Other'
            END AS CarColorGroup,
            CarModelYear,
            CarPrice
        FROM staging_raw;
    """)
    
    # Dim Supplier
    con.execute("""
        CREATE OR REPLACE TABLE dim_supplier AS
        SELECT DISTINCT
            SupplierID,
            SupplierName,
            SupplierAddress,
            SupplierContactDetails
        FROM staging_raw;
    """)
    
    # Dim Date
    con.execute("""
        CREATE OR REPLACE TABLE dim_date AS
        SELECT DISTINCT 
            CAST(date_val AS DATE) AS DateKey,
            EXTRACT(YEAR FROM CAST(date_val AS DATE)) AS Year,
            EXTRACT(MONTH FROM CAST(date_val AS DATE)) AS Month,
            EXTRACT(DAY FROM CAST(date_val AS DATE)) AS Day,
            EXTRACT(QUARTER FROM CAST(date_val AS DATE)) AS Quarter,
            DAYNAME(CAST(date_val AS DATE)) AS DayOfWeekName
        FROM (
            SELECT OrderDate AS date_val FROM staging_raw WHERE OrderDate IS NOT NULL
            UNION
            SELECT ShipDate AS date_val FROM staging_raw WHERE ShipDate IS NOT NULL
        ) AS all_dates;
    """)
    
def create_fact(con):
    # Fact Sale
    con.execute("""
        CREATE OR REPLACE TABLE fact_sales AS
        SELECT
            OrderID,
            CustomerID,
            ProductID,
            SupplierID,
            CAST(OrderDate AS DATE) AS OrderDateKey,
            CAST(ShipDate AS DATE) AS ShipDateKey,
            ShipMode,
            CreditCardType,
            CreditCard,
            CustomerFeedback,
            CAST(Sales AS DOUBLE) AS Sales,
            CAST(Quantity AS INTEGER) AS Quantity,
            CAST(Discount AS DOUBLE) AS Discount,
            Shipping
        FROM staging_raw;
    """)
    
def main():
    con = setup_connection()
    create_tables(con)
    create_dimensions(con)
    create_fact(con)
    con.close()
    
if __name__ == "__main__":
    main()