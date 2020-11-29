import elasticsearch


def search(query, _engine):

    query_body = {
        "query": {
            "bool": {
                "should": [
                    {
                        "match_phrase": {
                            "section": {
                                "query": query,
                                "boost": 6,
                                "slop": 10
                            }
                        }
                    },
                    {
                        "match": {
                            "section": {
                                "query": query,
                                "boost": 5,
                                "fuzziness": "AUTO"
                            }
                        }
                    },
                    {
                        "match": {
                            "title": {
                                "query": query
                            }
                        }
                    },
                    {
                        "match": {
                            "m_fulltext": {
                                "query": query,
                                "boost": 3,
                                "fuzziness": "AUTO"
                            }
                        }
                    }
                ]
            }
        }
    }

    if query.__contains__("*"):
        query_body['query']['bool']['should'].append({"wildcard": {"m_fulltext": {"value": query}}})

    out = _engine.search(index="testing-index", body=query_body)

    # repeat search with wildcard if nothing was found
    if out['hits']['total']['value'] < 1 and '*' not in query:
        return search(query + "*", _engine)

    return out


def process_out(output):

    def _print_output():
        print("============== Search results =================")
        print("Found: " + str(output['hits']['total']['value']))

        for out in output['hits']['hits']:
            print(str(out['_score'])[:7] + " => " + out['_source']['title'] + ": " + out['_source']['section'])
        print("================================================\n")

    _print_output()


if __name__ == "__main__":
    _ec = elasticsearch.Elasticsearch("localhost:9200")
    if _ec.ping():
        print("Connection established to localhost")
    else:
        print("Unable to establish connection to elastic")

    while True:
        text = input("search string: ")

        if text == "exit":
            exit()

        process_out(search(text, _ec))

