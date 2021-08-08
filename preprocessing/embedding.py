"""
This module contains functions to train word embeddings on an input corpus.
"""
from gensim.models import Word2Vec
from WordVectors import WordVectors
from nltk.tokenize import word_tokenize
import argparse


def main():
    w2v_params = {
        "vector_size": 100,
        "window": 5,
        "min_count": 10,
        "workers": 64
    }

    parser = argparse.ArgumentParser()
    parser.add_argument("input_corpus", type=str, help="Path to input corpus (sentencized)")
    parser.add_argument("output", type=str, help="Output embedding path")

    args = parser.parse_args()
    path_in = args.input_corpus
    path_out = args.output

    print("Reading corpus...")
    with open(path_in) as fin:
        sentences = [word_tokenize(s) for s in fin.readlines()]

    print("Training...")
    model = Word2Vec(sentences=sentences, **w2v_params)
    wv = WordVectors(words=model.wv.index_to_key, vectors=model.wv.vectors)

    wv.save_txt(path_out)


if __name__ == "__main__":
    main()

