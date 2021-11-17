import os
import json
import numpy as np
from WordVectors import WordVectors, intersection
from preprocessing.alignment import align

metadata = dict()


def load_wordvector(path, **kwargs):
    try:
        wv = WordVectors(input_file=path, **kwargs)
    except FileNotFoundError as e:
        print("WordVector file not found", e)
        raise

    return wv


def load_corpus(path):
    try:
        with open(path) as fin:
            sentences = list(map(lambda s: s.strip(), fin.readlines()))
    except FileNotFoundError as e:
        print("Corpus file not found", e)
        raise

    return sentences


def fetch_metadata(path):
    global metadata
    try:
        for file in os.listdir(path):
            with open(os.path.join(path, file)) as fin:
                d = json.load(fin)
                metadata[d["id"]] = d
        # Sort metadata based on `order` attribute
        output = sorted(list(metadata.values()), key=lambda s: s["order"] if "order" in s else 1000)
        print(output)
    except FileNotFoundError as e:
        print("File Not Found", e)
        raise

    return output


def handle_analysis(**params):
    global metadata
    try:
        if "normalize" in params:
            normalize = params["normalize"]
        else:
            normalize = False

        data_a = metadata[params["target_a"]]
        data_b = metadata[params["target_b"]]

        print("Loading word embeddings...")
        wv_a = load_wordvector(data_a["path_embeddings"], normalize=normalize)
        wv_b = load_wordvector(data_b["path_embeddings"], normalize=normalize)

        print("Loading sentences...")
        sentences_a = load_corpus(data_a["path_corpus"])
        sentences_b = load_corpus(data_b["path_corpus"])
    except ValueError as e:
        print(e)

    print("Aligning...")
    w_a, w_b = intersection(wv_a, wv_b)
    w_a, w_b, q = align(w_a, w_b)

    wv_a = np.dot(wv_a, q)
