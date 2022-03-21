"""
This module contains functions to train word embeddings on an input corpus.
"""
from gensim.models import Word2Vec
from .Tokenizer import tokenize_words
from .WordVectors import WordVectors
from nltk.tokenize import word_tokenize, sent_tokenize
import argparse
from multiprocessing import Pool


def cleanup_sentences(line, min_token_length=4):
    """
    called in parallel from cleanup corpus
    """
    # regex = re.compile("\W+")
    sents = sent_tokenize(line) # gives List[List[String]] with each List[String] = sentence
    sentences = list()
    for sent in sents:
        s = [t for t in tokenize_words(sent, min_length=min_token_length)]
        if len(s) > 0:
            sentences.append(s)

    return sentences


def cleanup_corpus(lines, workers=48):
    """
    Clean-up corpus by taking sentences and work tokens, removing non-word tokens.
    """

    with Pool(workers) as p:
        pool_sents = p.map(cleanup_sentences, lines)

    sentences = list()
    for s in pool_sents:
        sentences.extend(s)

    return sentences


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--vector_size", type=int, default=100, help="Size of embedding vectors")
    parser.add_argument("--window", type=int, default=5, help="Size of context windows")
    parser.add_argument("--min_count", type=int, default=20, help="Minimum word count")
    parser.add_argument("--workers", type=int, default=64, help="No. of worker threads")
    parser.add_argument("--input_corpus", type=str, help="Path to input corpus")
    parser.add_argument("--output", type=str, help="Path to output corpus")

    args = parser.parse_args()
    path_in = args.input_corpus
    path_out = args.output

    w2v_params = {
        "vector_size": args.vector_size,
        "window": args.window,
        "min_count": args.min_count,
        "workers": args.workers
    }

    print("Reading corpus...")
    with open(path_in) as fin:
        lines = fin.readlines()
    sentences = cleanup_corpus(lines, workers=args.workers)

    print("Training...")
    model = Word2Vec(sentences=sentences, **w2v_params)
    wv = WordVectors(words=model.wv.index_to_key, vectors=model.wv.vectors)

    wv.to_file(path_out)


if __name__ == "__main__":
    main()

