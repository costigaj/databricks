# =====================================================================
# Databricks PySpark & Spark SQL Common Operations Reference Guide
# =====================================================================
# This script contains commonly used code snippets for Databricks notebooks, 
# covering Catalogs, Schemas, Volumes, DBFS, CSV reading, Bronze Ingestion,
# Schema Evolution, Delta tables, and Silver Upserts.

from delta.tables import DeltaTable
from pyspark.sql import functions as F
from pyspark.sql.functions import current_timestamp

# ---------------------------------------------------------------------
# 1. CATALOGS, SCHEMAS, AND VOLUMES (Unity Catalog)
# ---------------------------------------------------------------------

# Create a Catalog using Spark SQL
spark.sql("CREATE CATALOG IF NOT EXISTS databricksac")

# Create Bronze and Silver Schemas (Databases) inside the Catalog
spark.sql("CREATE SCHEMA IF NOT EXISTS databricksac.bronze")
spark.sql("CREATE SCHEMA IF NOT EXISTS databricksac.silver")

# Create a Unity Catalog Volume for raw file landing
spark.sql("CREATE VOLUME IF NOT EXISTS databricksac.bronze.raw_files")


# ---------------------------------------------------------------------
# 2. DBFS / FOLDER OPERATIONS (using dbutils)
# ---------------------------------------------------------------------

# List contents of a Volume directory or DBFS path
# dbutils.fs.ls("/Volumes/databricksac/bronze/raw_files")

# Create a directory in DBFS
dbutils.fs.mkdirs("/dbutils/test_folder")


# ---------------------------------------------------------------------
# 3. READING A CSV FILE INTO A DATAFRAME
# ---------------------------------------------------------------------

csv_path = "/Volumes/databricksac/bronze/raw_files/sample_data.csv"

# Read CSV with header and inferred schema
df_raw = (
    spark.read.format("csv")
    .option("header", "true")
    .option("inferSchema", "true")
    .load(csv_path)
)

# Display sample rows
df_raw.display()


# ---------------------------------------------------------------------
# 4. BRONZE INGESTION LAYER (Append-Only Raw Landing)
# ---------------------------------------------------------------------

# Tag raw data with an ingestion timestamp before saving to Bronze
df_bronze = df_raw.withColumn("IngestedDate", current_timestamp())

# Append immutable raw records into the Bronze Delta table
df_bronze.write.format("delta") \
    .mode("append") \
    .saveAsTable("databricksac.bronze.customers_raw")


# ---------------------------------------------------------------------
# 5. SCHEMA ENFORCEMENT & EVOLUTION
# ---------------------------------------------------------------------

# Delta Lake enforces schema by default and blocks mismatched columns.
# Use mergeSchema = "true" when adding new columns to an existing Delta table:
df_bronze.write.format("delta") \
    .mode("append") \
    .option("mergeSchema", "true") \
    .saveAsTable("databricksac.bronze.customers_raw")

# For Delta MERGE (Upsert) operations, enable automatic schema evolution:
# spark.conf.set("spark.databricks.delta.schema.autoMerge.enabled", "true")


# ---------------------------------------------------------------------
# 6. CREATING / OVERWRITING DELTA TABLES (Silver Layer)
# ---------------------------------------------------------------------

# Save a DataFrame directly as a managed Delta table (Full Overwrite)
# df.write.format("delta") \
#     .mode("overwrite") \
#     .saveAsTable("databricksac.silver.customers_enr")


# ---------------------------------------------------------------------
# 7. TRANSFORMATIONS & AUDIT COLUMNS (Preparing for Silver)
# ---------------------------------------------------------------------

# Read from Bronze (or use transformed DataFrame) and tag with ProcessedDate
df = spark.table("databricksac.bronze.customers_raw")
df = df.withColumn("ProcessedDate", current_timestamp())
display(df)


# ---------------------------------------------------------------------
# 8. SILVER UPSERT (MERGE) PATTERN INTO DELTA TABLES
# ---------------------------------------------------------------------

target_table_name = "databricksac.silver.customers_enr"

if spark.catalog.tableExists(target_table_name):
    print("--- Table exists: Executing Delta MERGE (Upsert) ---")
    
    dlt_object = DeltaTable.forName(spark, target_table_name)

    # Perform MERGE based on customer_id
    dlt_object.alias("t") \
        .merge(df.alias("s"), "t.customer_id = s.customer_id") \
        .whenMatchedUpdateAll() \
        .whenNotMatchedInsertAll() \
        .execute()
else:
    print("--- Table does not exist: Executing initial creation (Append) ---")
    
    df.write.format("delta") \
        .mode("append") \
        .saveAsTable(target_table_name)
