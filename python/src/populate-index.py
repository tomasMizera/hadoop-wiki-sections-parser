from elasticsearch import helpers, Elasticsearch
import json
import glob
import sys
import os


def _connect_elastic():
    print("connecting to elastic...")

    _es = None
    _es = Elasticsearch([
        {
            'host': 'localhost',
            'port': 9200
         }
    ])

    if _es.ping():
        print("Connection established to localhost!")
    else:
        print("Unable to establish connection to elastic!")
        exit()

    return _es


def _get_file_names(_in_dir):
    files = glob.glob(os.path.join(_in_dir, "part*"))
    return files


def process_files(files, es_client, index):

    def _process_file(_file):
        with open(_file, 'r') as f:
            for page in f.readlines():
                print(page)
                page = json.loads(page)
                if not page.get("sections", None):
                    continue
                title = page["title"].strip()
                sections = page["sections"]
                for section in sections:
                    yield {
                        "_index": index,
                        "title": title,
                        "section": section.strip(),
                        "m_fulltext": title + " " + section.strip()
                    }

    for file in files:
        print("Processing file " + file)
        out = helpers.bulk(es_client, _process_file(file))
        print(f'Processed file {file}, results: ' + str(out))


if len(sys.argv) < 3:
    print("Please provide path to input files directory and index name")
    exit()

_in_path = sys.argv[1]
_index = sys.argv[2]

if __name__ == "__main__":
    client = _connect_elastic()
    # process_files(_get_file_names(_in_path), client, _index)
    process_files(['/home/tomasmizera/school/vinf/raw-data/testing/aaa.ndjson'], client, _index)
