"""
Functions for pre-processing and clean-up of input corpora.
"""
from nltk.tokenize import sent_tokenize, word_tokenize
import argparse


def sentencize_document(document):
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


def save_file(path, sentences):
    """
    Write a text file to `path` containing each sentence from `sentences` in a line.
    Args:
        path (str) - Path to output file.
        sentences (list) - List of tokenized sentences to write out.
    Return:
    """
    with open(path, "w") as fout:
        for sent in sentences:
            fout.write("%s\n" % " ".join(sent))


def main():

    path_in = "../../data/coca/coca_all.txt"
    path_out = "../../data/corpus/coca-sent.txt"

    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=str, help="Path to input corpus")
    parser.add_argument("output", type=str, help="Output path to sentencized corpus")

    args = parser.parse_args()

    path_in = args.input
    path_out = args.output

    with open(path_in) as fin:
        text = "\n".join(fin.readlines())

    print("Processing...")
    sentences = sentencize_document(text)
    save_file(path_out, sentences)


if __name__ == "__main__":
    main()