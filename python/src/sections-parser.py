from pyspark.sql import SparkSession
from pyspark.sql.types import *
import re
import argparse
from functools import reduce
import json as JSON

argparser = argparse.ArgumentParser(description="Spark application", usage="Use with Spark-Submit.sh")
argparser.add_argument('in', help="Input xml file")
argparser.add_argument('out', help="Output directory")
argparser.add_argument('--master-addr', help="Spark master address")
argparser.add_argument('--spark', help="Spark executor uri")
argparser.add_argument('--app-name', help="Application name, default mizera.spark.wiki")
args = vars(argparser.parse_args())

app = args.get("--app-name", "mizera.spark.wiki")
master_addr = args.get("--master-addr", "spark://tomasmizera:7077")
filein = args.get("in")
outdir = args.get("out")

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

# set a logger
log4jLogger = spark._jvm.org.apache.log4j
LOGGER = log4jLogger.LogManager.getLogger(__name__)

LOGGER.info("About to open file " + filein + " ...")
df = spark.read.format("com.databricks.spark.xml") \
    .option("rowTag", "page") \
    .load(filein, schema=customSchema)

LOGGER.info("File opened")

dfRDD = df.rdd

LOGGER.info("Started parsing sections ...")


def parse_section(row):
    json = {'hash': row.revision.sha1, 'title': row.title}
    raw_text = row.revision.text
    text_chunks = re.findall("([=]{2})([A-Za-z0-9,\-_:\.`;' ]+)([=]{2})[^=]", raw_text)
    amap = map(lambda x: list(filter(lambda y: not y.startswith('=='), x)), text_chunks)
    amap = reduce(lambda a, b: a + b, amap, [])
    if len(amap) > 0:
        json['sections'] = amap
        return JSON.dumps(json)


dfRDD \
    .map(parse_section) \
    .filter(lambda x: x) \
    .repartition(10) \
    .saveAsTextFile(outdir)

LOGGER.info("Parsing done, saved")


