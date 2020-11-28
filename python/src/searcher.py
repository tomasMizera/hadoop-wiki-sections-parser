import elasticsearch as EC


def search(query, _engine):

    query_body = {
        "query": {
            "match": {
                "sections": {
                    "query": query,
                    "fuzziness": "AUTO"
                }
            }
        }
    }

    return _engine.search(index="financial", body=query_body)


def process_out(output):
    print("Found: " + str(output['hits']['total']['value']))

    for out in output['hits']['hits']:
        print(out['_source']['title'])
        print(out['_source']['sections'])
        print()


if __name__ == "__main__":
    _ec = EC.Elasticsearch("localhost:9200")
    if _ec.ping():
        print("Connection established to localhost")
    else:
        print("Unable to establish connection to elastic")

    while True:
        text = input("search string: ")

        if text == "exit":
            exit()

        process_out(search(text, _ec))

