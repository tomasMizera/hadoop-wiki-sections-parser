import elasticsearch as EC


def _connect_elastic():
    print("... connecting to elastic")

    _es = None
    _es = EC.Elasticsearch([
        {
            'host': 'localhost',
            'port': 9200
         }
    ])

    if _es.ping():
        print("Connection established to localhost")
    else:
        print("Unable to establish connection to elastic")

    return _es


if __name__ == "__main__":
    client = _connect_elastic()
    # TODO:
    # 1. iterate over input folder with glob
    # 2. read files one by one
    # 3. read each line
    # 4. for each document do a generator that has only one section with title
    # 5. push it into bulk arr
    # 6. bulk insert file
    # 7. repeat process from 2.