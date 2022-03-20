import os
from preprocessing.WordVectors import WordVectors, intersection
from app.preprocessing.generate_examples.alignment.global_align import align
from preprocessing.mapping import perform_mapping
from app.preprocessing.generate_examples.alignment.noise_aware import noise_aware
import app.preprocessing.generate_examples.alignment.s4 as s4
import pickle
import argparse
import numpy as np


class Globals:
    def __init__(self):
        self.wv1 = dict()
        self.wv2 = dict()
        self.sorted_words = None
        self.distances_ab = dict()
        self.indices_ab = dict()
        self.distances_ba = dict()
        self.indices_ba = dict()
        self.anchors = dict()
        self.d = dict()
        self.common = 0
        self.filename1 = "A"
        self.filename2 = "B"
        self.sents1 = list()
        self.sents2 = list()
        self.sent_vecs1 = None
        self.sent_vecs2 = None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("a", type=str, help="Path to embedding A")
    parser.add_argument("b", type=str, help="Path to embedding B")
    parser.add_argument("corpus_a", type=str, help="Path to corpus A")
    parser.add_argument("corpus_b", type=str, help="Path to corpus B")
    parser.add_argument("output", type=str, help="Path to save output")
    parser.add_argument("--k_neighbors", type=int, default=50, help="Number of neighbors to include in the analysis.")
    parser.add_argument("--n_samples", type=int, default=200000, help="Number of sentences to sample from each corpus.")
    args = parser.parse_args()

    g = Globals()

    g.filename1 = os.path.basename(args.a)
    g.filename2 = os.path.basename(args.b)

    wv1_full = WordVectors(input_file=args.a)
    wv2_full = WordVectors(input_file=args.b)

    wv1, wv2 = intersection(wv1_full, wv2_full)

    # Parameters
    k = args.k_neighbors

    g.common = len(wv1)

    # Use global anchors
    g.wv1["global"], g.wv2["global"], _ = align(wv1, wv2)
    g.anchors["global"] = wv1.words
    words = wv1.words
    g.sorted_words = sorted(words)
    g.distances_ab["global"], g.indices_ab["global"] = perform_mapping(g.wv1["global"],
                                                                       g.wv2["global"], k=k)
    g.distances_ba["global"], g.indices_ba["global"] = perform_mapping(g.wv2["global"],
                                                                       g.wv1["global"], k=k)

    anchors, non_anchors, _ = s4.s4(wv1, wv2, verbose=1, iters=100)
    g.anchors["s4"] = anchors
    g.wv1["s4"], g.wv2["s4"], _ = align(wv1, wv2, anchor_words=anchors)
    # Mapping
    g.distances_ab["s4"], g.indices_ab["s4"] = perform_mapping(g.wv1["s4"], g.wv2["s4"], k=k)
    g.distances_ba["s4"], g.indices_ba["s4"] = perform_mapping(g.wv2["s4"], g.wv1["s4"], k=k)

    # Get noise-aware anchors
    _, alpha, anchors, non_anchors = noise_aware(wv1.vectors, wv2.vectors)
    g.anchors["noise-aware"] = anchors
    g.wv1["noise-aware"], g.wv2["noise-aware"], _ = align(wv1, wv2, anchor_words=anchors)
    g.distances_ab["noise-aware"], g.indices_ab["noise-aware"] = \
        perform_mapping(g.wv1["noise-aware"], g.wv2["noise-aware"], k=k)
    g.distances_ba["noise-aware"], g.indices_ba["noise-aware"] = \
        perform_mapping(g.wv2["noise-aware"], g.wv1["noise-aware"], k=k)

    # Collect sentences from corpora
    with open(args.corpus_a) as fin:
        g.sents1 = [s.rstrip() for s in fin.readlines()]
    with open(args.corpus_b) as fin:
        g.sents2 = [s.rstrip() for s in fin.readlines()]

    np.random.seed(0)

    if len(g.sents1) > args.n_samples:
        samples_1 = np.random.choice(len(g.sents1), size=args.n_samples)
        g.sents1 = [g.sents1[i] for i in samples_1]
    if len(g.sents2) > args.n_samples:
        samples_2 = np.random.choice(len(g.sents2), size=args.n_samples)
        g.sents2 = [g.sents2[i] for i in samples_2]

    with open(args.output, "wb") as fout:
        pickle.dump(g, fout)


if __name__ == "__main__":
    main()
