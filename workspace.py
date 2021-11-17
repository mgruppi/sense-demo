import os
import json
import numpy as np
from WordVectors import WordVectors, intersection
from preprocessing.alignment import align
from scipy.spatial.distance import cosine, euclidean
from sklearn.neighbors import NearestNeighbors
from sklearn.decomposition import PCA

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
        sentences = list()
        with open(path) as fin:
            sentences = list(map(lambda s: s.strip(), fin.readlines()))
    except FileNotFoundError as e:
        print("Corpus file not found", e)

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


def find_top_shifted(wv_a, wv_b):
    """
    Returns the list of most shifted words between WordVectors a and b.
    Args:
        wv_a, wv_b: WordVectors objects
    Returns:
        indices, distances - Lists of indices and their semantic distances sorted from most to least shifted
    """

    d = np.array([cosine(u, v) for u, v in zip(wv_a.vectors, wv_b.vectors)])

    indices = np.argsort(d)[::-1]
    distances = d[indices]
    return indices, distances


def pca_decomposition(u, v):
    """
    Performs 2D PCA decomposition of embedding matrices `u` and `v`.
    Args:
          u,v - embedding matrices
    Returns:
          x_u, x_v - the PCA decomposition of `u` and `v`.
    """
    pca = PCA(n_components=2)
    pca.fit(u)
    pca.fit(v)
    x_u = pca.transform(u)
    x_v = pca.transform(v)

    return x_u, x_v


def handle_analysis(**params):
    global metadata
    try:
        if "normalize" in params:
            normalize = True if params["normalize"] == "true" else False
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
    except KeyError as e:
        print("Error reading dataset", e)
        raise

    print("Aligning...")
    w_a, w_b = intersection(wv_a, wv_b)
    w_a, w_b, q = align(w_a, w_b)
    wv_a = np.dot(wv_a, q)

    print("Most Shifted")
    indices, distances = find_top_shifted(w_a, w_b)
    print(w_a.words[indices])
    print(distances)

    x_a, x_b = pca_decomposition(w_a.vectors, w_b.vectors)

    data = {
                "most_shifted": {"indices": indices.tolist(), "distances": distances.tolist()},
                "common_vocabulary": w_a.words.tolist(),
                "vectors": {"x_a": x_a.tolist(), "x_b": x_b.tolist()},
           }
    return data
