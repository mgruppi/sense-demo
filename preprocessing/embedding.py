"""
This module contains functions to train word embeddings on an input corpus.
"""
from gensim.models import Word2Vec
from nltk.tokenize import sent_tokenize, word_tokenize
from WordVectors import WordVectors


def process_corpus(document):
    """
    Processing of input `document`, given as a string.
    The input document is sentence-tokenized using NLTK's `sent_tokenize` and word-tokenize using NLTK's `word_tokenize`
    Args:
        document (str) - Document to be processed.
    Return:
        sents (list) - Sentences as lists of tokens.
    """
    sents = sent_tokenize(document.lower())
    sents = [word_tokenize(s) for s in sents]

    return sents


def main():
    w2v_params = {
        "vector_size": 100,
        "window": 5,
        "min_count": 10,
        "workers": 64
    }

    with open("../../data/bnc/bnc.txt") as fin:
        text = "\n".join(fin.readlines())

    print("Processing...")
    sentences = process_corpus(text)

    print("Training...")
    model = Word2Vec(sentences=sentences, **w2v_params)
    wv = WordVectors(words=model.wv.index_to_key, vectors=model.wv.vectors)


if __name__ == "__main__":
    main()

