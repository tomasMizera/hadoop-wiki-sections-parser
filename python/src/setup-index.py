import elasticsearch as EC
import sys


def _connect_elastic():
    print("... connecting to elastic")

    _es = None
    _es = EC.Elasticsearch([
        {
            'host': 'localhost',
            'port': 9200
         }
    ])

    return _es


def _create_index(mapping, index, _es):
    print("... creating index " + indexname)
    try:
        if not _es.indices.exists(index):
            _es.indices.create(index=index, ignore=400, body=mapping)
            print('index created!')
        return True
    except Exception as ex:
        print('could not create index\n', str(ex))
        return False


def _get_mapping():

    mapping = {
        "settings": {
            "number_of_shards": 1,
            "number_of_replicas": 0
        },
        "mappings": {
            "members": {
                "dynamic": "strict",
                "properties": {
                    "hash": {
                        "type": "text"
                    },
                    "title": {
                        "type": "text"
                    },
                    "sections": {
                        "type": "text"
                    }
                }
            }
        }
    }

    return mapping


indexname = sys.argv[1] if len(sys.argv) > 1 else "test-index"

if __name__ == "__main__":
    elastic = _connect_elastic()
    if elastic:
        print("elastic connected!")
        _create_index(_get_mapping(), indexname, elastic)
    else:
        print("unable to connect")

