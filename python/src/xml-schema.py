from pyspark.sql import SparkSession
from pyspark.sql.types import *
import argparse

argparser = argparse.ArgumentParser(description="Spark application", usage="Use with Spark-Submit.sh")
argparser.add_argument('in', help="Input xml file")
argparser.add_argument('out', help="Output directory")
argparser.add_argument('--master-addr', help="Spark master address")
argparser.add_argument('--spark', help="Spark executor uri")
argparser.add_argument('--app-name', help="Application name, default mizera.spark.wiki")
args = vars(argparser.parse_args())

app = args.get("--app-name", "mizera.spark.wiki")
master_addr = args.get("--master-addr", "spark://tomasmizera:7077")

# Create Spark session
spark = None

if args.get('--spark', None):
    spark = SparkSession.builder \
        .config("spark.executor.uri", args.get('--spark')) \
        .appName(app) \
        .master(master_addr) \
        .getOrCreate()
else:
    spark = SparkSession.builder \
        .appName(app) \
        .master(master_addr) \
        .getOrCreate()


customSchema = StructType([
    StructField("title", StringType(), True),
    StructField("revision", StructType([
        StructField("text", StringType(), True),
        StructField("sha1", StringType(), True),
    ]), True)
])

# This needs to be added!
# .config("spark.executor.uri", "hdfs://147.213.75.180/user/hadmin/pyspark.tgz")

filein = vars(args)['in']

df = spark.read.format("com.databricks.spark.xml") \
    .option("rowTag","page") \
    .load(filein, schema=customSchema)

