# Mapper 

# import beautifulSoup4 as bs

import sys

# input from standard input ~ HMTL sites from HDFS

for site in sys.stdin:

    parser = bs.beautifulSoup4(site, type="HTML")
    
    # get sections from parser
    parser.find(" SECTION TAG ")
    
    # probably some preprocessing 

    for section in sections:
        
        # pass section via standard output to reducer.
        print( section )

