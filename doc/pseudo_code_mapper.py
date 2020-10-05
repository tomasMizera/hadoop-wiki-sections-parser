# Mapper 

# import databricks_py

import sys
import xml

# input from standard input ~ HMTL sites from HDFS

for site in sys.stdin:

    parser = databricks( input )
    
    # get sections from parser
    sections = find(" === SECTION TAG === ", parser)
    
    # probably some preprocessing 

    for section in sections:
        
        # pass section via standard output to reducer.
        print( section )

