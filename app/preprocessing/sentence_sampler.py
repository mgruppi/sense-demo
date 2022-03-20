import argparse
import pickle
import numpy as np

from preprocessing.generate_sentences import Globals

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=str, help="Input pickle")
    parser.add_argument("output", type=str, help="Output pickle")
    parser.add_argument("--n", default=200000, type=int, help="Number of sentences to sample")

    args = parser.parse_args()

    with open(args.input, "rb") as fin:
        data = pickle.load(fin)

    np.random.seed(0)

    samples_1 = np.random.choice(len(data.sents1), size=args.n)
    samples_2 = np.random.choice(len(data.sents2), size=args.n)

    data.sents1 = [data.sents1[i] for i in samples_1]
    data.sents2 = [data.sents2[i] for i in samples_2]

    with open(args.output, "wb") as fout:
        pickle.dump(data, fout)