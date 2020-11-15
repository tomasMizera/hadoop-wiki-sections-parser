from pyspark.sql.column import Column, _to_java_column
from pyspark.sql.types import _parse_datatype_json_string
from pyspark.sql import SparkSession
import re
import sys
from functools import reduce

# functions will be used for nexted xml parsing
# from databricks example python scala API porting https://github.com/databricks/spark-xml
def ext_from_xml(xml_column, schema, options={}):
    java_column = _to_java_column(xml_column.cast('string'))
    java_schema = spark._jsparkSession.parseDataType(schema.json())
    scala_map = spark._jvm.org.apache.spark.api.python.PythonUtils.toScalaMap(options)
    jc = spark._jvm.com.databricks.spark.xml.functions.from_xml(
        java_column, java_schema, scala_map)
    return Column(jc)


# from databricks example python scala API porting https://github.com/databricks/spark-xml
def ext_schema_of_xml_df(df, options={}):
    assert len(df.columns) == 1

    scala_options = spark._jvm.PythonUtils.toScalaMap(options)
    java_xml_module = getattr(getattr(
        spark._jvm.com.databricks.spark.xml, "package$"), "MODULE$")
    java_schema = java_xml_module.schema_of_xml_df(df._jdf, scala_options)
    return _parse_datatype_json_string(java_schema.json())


app = "Read initial wiki page"
master_addr = "spark://tomasmizera:7077"

# Create Spark session
spark = SparkSession.builder \
    .appName(app) \
    .master(master_addr) \
    .getOrCreate()


# set logger
log4jLogger = spark._jvm.org.apache.log4j
LOGGER = log4jLogger.LogManager.getLogger(__name__)

if len( sys.argv ) < 2:
    LOGGER.info("Not enough arguments passed to script! Should be <input path> and <output path>")
    exit()

filein = sys.argv[1]
fileout = sys.argv[2]

LOGGER.info("About to open file " + filein + " ...")
df = spark.read.format("com.databricks.spark.xml") \
    .option("rowTag","revision") \
    .load(filein)

df.show()

LOGGER.info("File opened")

textRDD = df.select("text").rdd

LOGGER.info("Started parsing sections ...")


def parse_section(text):
    raw_text = text.text._VALUE
    text_chunks = re.findall("([=]{2})([A-Za-z0-9,\-_:\.`;' ]+)([=]{2})[^=]", raw_text)

    # we have a list of tuples that contain catched groups
    amap = map(lambda x: list(filter(lambda y: not y.startswith('=='), x)),text_chunks)

    return reduce( lambda a, b: a+b, amap, [] )

textRDD\
    .map(parse_section)\
    .filter(lambda x: x)\
    .repartition(10)\
    .saveAsTextFile(fileout)

LOGGER.info("Parsing done, saved")


