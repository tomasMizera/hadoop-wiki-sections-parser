from pyspark.sql.column import Column, _to_java_column
from pyspark.sql.types import _parse_datatype_json_string
from pyspark.sql import SparkSession
import pandas as pd
import re


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

# TODO: pass file as argument to spark-submit instead of hardcoded path
filepath = "file:///home/tomasmizera/school/vinf/data/single-page-revision.xml"

LOGGER.info("About to open file " + filepath + " ...")
df = spark.read.format("com.databricks.spark.xml") \
    .option("rowTag","revision") \
    .load(filepath)

df.show()

LOGGER.info("File opened")

dfp = df.select("text").toPandas() #convert spark dataframe to pandas df

# by default text was set as index
dfp = dfp.reset_index()

# now get text, we only have one article in test data
text = dfp.iloc[0].text[0] # Spark Row class to str

assert( type(text) is str )

LOGGER.info("Started parsing sections ...")

# now get article tags by splitting with regex
# TODO: fix regex to not match nested sections
text_chunks = re.split("(==[A-Za-z0-9,-_:.`;' ]+==)", text)

# we now have array holding section title, text, section title, text,...
# convert it to dict
sections = {}


class Section:
    def __init__(self, _sectionname, _sectiontext):
        self.articletitle = None
        self.sectionname = _sectionname
        self.sectiontext = _sectiontext

    def __str__(self):
        return "-----\n" + self.sectionname + "\n" + self.sectiontext[:30] + "..."


iterator = 0
if len(text_chunks) > 1:
    # there can be some junk text before first section name
    if not text_chunks[0].startswith("="):
        text_chunks.pop(0)

    for iterator in range (len(text_chunks)):
        if text_chunks[iterator].startswith("="):
            sections[iterator] = \
                Section(text_chunks[iterator], text_chunks[iterator + 1 ])

LOGGER.info("Parsing done")

# print the result
prnt = lambda x: print(x)
{key: prnt(section) for key, section in sections.items()}

