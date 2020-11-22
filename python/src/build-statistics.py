import sys
import glob
from os import path as PATH
# import nltk
import json as JSON
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords
# import gc

if len(sys.argv) < 2:
    print("Please provide path to directory")
    exit()

path = sys.argv[1]
analyzer = None

# defines for computing stats
DF = 0
CF = 1
stats = {}
stop_words = set(stopwords.words('english'))


def stemma_lemma():
    return WordNetLemmatizer()


def _get_file_names(_in_dir):
    files = glob.glob(PATH.join(_in_dir, "part*"))
    return files


def parse_section(section):
    if not section or not analyzer:
        return

    tokens = word_tokenize(section)
    for token in tokens:
        if token not in stop_words:
            t = analyzer.lemmatize(token.lower())  # depends on lemmatizer or stemmer
            # t = analyzer.stem(token.lower())
            stats[t] = stats[t] + 1 if stats.get(t, None) else 1


def parse_document(doc):
    if not doc or not doc.get("sections", None):
        return

    # iterate over array of sections and parse each section
    for section in doc.get("sections", []):
        parse_section(section)


def _merge_dicts(_):
    pass


def process_files(files):
    global stats
    for file in files:
        print("...processing file " + file)

        f = open(file, "r")
        for line in f.readlines():
            parse_document(JSON.loads(line))  # here we consider page as document
        f.close()
        # stats = _merge_dicts(stats_file, stats)
        # gc.collect()
        print(f'file {file} processed!')

    print('done processing files! saving..')

    with open('stats.json', 'w') as f:
        cf = {"cf": stats}
        JSON.dump(cf, f)
        print('saved!')


if __name__ == "__main__":
    analyzer = stemma_lemma()
    process_files(_get_file_names(path))
