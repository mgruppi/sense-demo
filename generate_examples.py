import os
import numpy as np
from WordVectors import WordVectors, intersection
from scipy.spatial.distance import cosine
from alignment import align
from mapping import perform_mapping
from noise_aware import noise_aware
import s4
import pickle
import argparse


class Globals:
    def __init__(self):
        self.wv1 = dict()
        self.wv2 = dict()
        self.sorted_words = None
        self.distances_ab = dict()
        self.indices_ab = dict()
        self.distances_ba = dict()
        self.indices_ba = dict()
        self.d = dict()
        self.common = 0
        self.filename1 = "A"
        self.filename2 = "B"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("a", type=str, help="Path to embedding A")
    parser.add_argument("b", type=str, help="Path to embedding B")
    parser.add_argument("output", type=str, help="Path to save output")
    parser.add_argument("--k_neighbors", type=int, default=50, help="Number of neighbors to include in analysis.")
    args = parser.parse_args()

    g = Globals()

    g.filename1 = os.path.basename(args.a)
    g.filename2 = os.path.basename(args.b)

    wv1 = WordVectors(input_file=args.a)
    wv2 = WordVectors(input_file=args.b)

    wv1, wv2 = intersection(wv1, wv2)

    # Parameters
    k = args.k_neighbors

    g.common = len(wv1)

    # Use global anchors
    g.wv1["global"], g.wv2["global"], _ = align(wv1, wv2)
    words = wv1.words
    g.sorted_words = sorted(words)
    g.distances_ab["global"], g.indices_ab["global"] = perform_mapping(g.wv1["global"],
                                                                        g.wv2["global"], k=k)
    g.distances_ba["global"], g.indices_ba["global"] = perform_mapping(g.wv2["global"],
                                                                        g.wv1["global"], k=k)

    anchors, non_anchors, _ = s4.s4(wv1, wv2, verbose=1, iters=100)
    g.wv1["s4"], g.wv2["s4"], _ = align(wv1, wv2, anchor_words=anchors)
    # Mapping
    g.distances_ab["s4"], g.indices_ab["s4"] = perform_mapping(g.wv1["s4"], g.wv2["s4"], k=k)
    g.distances_ba["s4"], g.indices_ba["s4"] = perform_mapping(g.wv2["s4"], g.wv1["s4"], k=k)

    # Get noise-aware anchors
    _, alpha, anchors, non_anchors = noise_aware(wv1.vectors, wv2.vectors)
    g.wv1["noise-aware"], g.wv2["noise-aware"], _ = align(wv1, wv2, anchor_words=anchors)
    g.distances_ab["noise-aware"], g.indices_ab["noise-aware"] = \
        perform_mapping(g.wv1["noise-aware"], g.wv2["noise-aware"], k=k)
    g.distances_ba["noise-aware"], g.indices_ba["noise-aware"] = \
        perform_mapping(g.wv2["noise-aware"], g.wv1["noise-aware"], k=k)

    with open(args.output, "wb") as fout:
        pickle.dump(g, fout)


if __name__ == "__main__":
    main()