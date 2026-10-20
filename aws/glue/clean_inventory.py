"""AWS Glue PySpark starter: clean and aggregate grocery CSV data."""
from pyspark.sql import SparkSession, functions as F

spark = SparkSession.builder.getOrCreate()
RAW_ROOT = "s3://YOUR-BUCKET/raw"
CLEAN_ROOT = "s3://YOUR-BUCKET/cleaned"

inventory = spark.read.option("header", True).csv(f"{RAW_ROOT}/inventory/")
sales = spark.read.option("header", True).csv(f"{RAW_ROOT}/sales/")

inventory = (
    inventory
    .withColumn("quantity_on_hand", F.col("quantity_on_hand").cast("int"))
    .withColumn("unit_cost", F.col("unit_cost").cast("double"))
    .withColumn("expiry_date", F.to_date("expiry_date", "yyyy-MM-dd"))
    .withColumn("batch_id", F.trim(F.col("batch_id")))
    .withColumn("product_id", F.trim(F.col("product_id")))
    .dropDuplicates(["batch_id"])
    .filter(F.col("batch_id").isNotNull() & F.col("product_id").isNotNull())
    .filter((F.col("quantity_on_hand") >= 0) & (F.col("unit_cost") >= 0))
    .filter(F.col("expiry_date").isNotNull())
)

sales = (
    sales
    .withColumn("sale_date", F.to_date("sale_date", "yyyy-MM-dd"))
    .withColumn("units_sold", F.col("units_sold").cast("int"))
    .withColumn("product_id", F.trim(F.col("product_id")))
    .filter(F.col("sale_date").isNotNull() & F.col("product_id").isNotNull())
    .filter(F.col("units_sold") >= 0)
)

daily_sales = (
    sales.groupBy("product_id", "sale_date")
    .agg(F.sum("units_sold").alias("units_sold"))
)

inventory.write.mode("overwrite").parquet(f"{CLEAN_ROOT}/inventory/")
daily_sales.write.mode("overwrite").parquet(f"{CLEAN_ROOT}/daily_sales/")
