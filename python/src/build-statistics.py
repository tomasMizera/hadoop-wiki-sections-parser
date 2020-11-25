import sys
import glob
from os import path as PATH
import json as JSON
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
from collections import Counter

if len(sys.argv) < 3:
    print("Please provide path to directory and out file")
    exit()

path = sys.argv[1]
path_out = sys.argv[2]
analyzer = None

# defines for computing stats
DF = 0
CF = 1
stats = {}
stop_words = set(stopwords.words('english'))
# stop_words = stop_words + {','}


def stemma_lemma():
    return WordNetLemmatizer()


def _get_file_names(_in_dir):
    files = glob.glob(PATH.join(_in_dir, "part*"))
    return files


def process_document(section):
    if not section or not analyzer:
        return

    tokens = word_tokenize(section)
    tokens = list(map(lambda t: t.lower(), tokens))
    tokens = list(filter(lambda t: t not in stop_words, tokens))
    tokens = list(map(lambda t: analyzer.lemmatize(t), tokens))
    tokens_counter = Counter(tokens)

    # count frequencies
    for token in tokens_counter.keys():
        if stats.get(token, None):
            stats[token]["cf"] = stats[token]["cf"] + tokens_counter[token]
            stats[token]["df"] += 1
        else:
            stats[token] = {"cf": tokens_counter[token], "df": 1}


def process_page(doc):
    if not doc or not doc.get("sections", None):
        return

    # iterate over array of sections and parse each section
    for section in doc.get("sections", []):
        process_document(section)  # here we consider section as a document


def _sort_func():
    pass


def process_files(files):
    global stats
    for file in files:
        print("...processing file " + file)

        f = open(file, "r")
        for line in f.readlines():
            process_page(JSON.loads(line))
        f.close()
        print(f'file {file} processed!')

    print('done processing files! saving..')

    with open(path_out, 'w') as f:
        # sort items by document frequency
        stats = {k: v for k, v in sorted(stats.items(), key=lambda item: item[1]["df"], reverse=True)}
        JSON.dump(stats, f)
        f.close()
        print('saved!')


if __name__ == "__main__":
    analyzer = stemma_lemma()
    process_files(_get_file_names(path))
