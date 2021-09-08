import numpy as np
from sklearn.metrics import pairwise_distances


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
        self.sents1 = list()
        self.sents2 = list()
        self.sent_vecs1 = None
        self.sent_vecs2 = None


def sentence_to_vec(sent, wv):
    """
    Transforms a sentence into a vector.
    This is done by averaging the word embeddings of the sentence using WordVectors `wv`.
    Out of vocabulary tokens are ignored.
    Args:
        sent (str): Input sentence.
        wv (WordVectors): Embeddings used to encode `sent`.
    """

    x = np.zeros(wv.dimension, dtype=np.float32)

    tokens = sent.split(" ")
    for token in tokens:
        if token in wv:
            x += wv[token]
    return x


def get_sentence_distances(x_src, x_tgt):
    """
    Given a sentence vector `x_srx` and a list of sentence vectors `x_t`, find the best example candidates from x_t
    to be used as sentence examples.
    The best candidates are the less similar (distant) points in `x_t` to `x_src`.
    Args:
        x_src: np.array(d) - the source vector
        x_tgt: np.array(n x d) - the list/matrix of target vectors
    Returns:
        distances, indices: distances and indices from high to low
    """
    d = pairwise_distances(x_src, x_tgt, metric="cosine")
    return d


def generate_sentence_samples(model, target, case_sensitive=False, n_samples=5):
    """
    Given a model of `Globals` containing embeddings from corpus_a and corpus_b, retrieve samples of sentences that
    are distinct based on the sentence embedding distance.
    The sentence embedding is computed by averaging the word embeddings of a sentence using vectors trained on
    the respective corpus. E.g.: given sentence `s` in corpus_a, sentence representation is given by averaging
    wv_a(w) for w in `s`.
    Args:
        model: Demo model (pickle).
        target: Word to extract sentences for.
        case_sensitive: Toggle case sensitivity True or False (default: False).
        n_samples: Number of sentence samples to return.
    Returns:
        sents_a: List of sentences from source A.
        sents_b: List of sentences from source B.
        samples_a: Indices of sents_b that best match each sentence in sents_a.
        samples_b: Indices of sents_a sentences for sentences in sents_b.
    """

    # These lists store sentences containing the target word in each corpus.
    sent_ids_a = list()
    sent_ids_b = list()

    if not case_sensitive:
        def case(s):
            return s.lower()
    else:
        target = target.lower()

        def case(s):
            return s

    for i, sent in enumerate(model.sents1):
        tokens = [case(r) for r in sent.rstrip().split(" ")]
        if target in set(tokens):
            sent_ids_a.append(i)

    for i, sent in enumerate(model.sents2):
        tokens = [case(r) for r in sent.rstrip().split(" ")]
        if target in set(tokens):
            sent_ids_b.append(i)

    x_a = [sentence_to_vec(model.sents1[i], model.wv1["s4"]) for i in sent_ids_a]
    x_b = [sentence_to_vec(model.sents2[i], model.wv2["s4"]) for i in sent_ids_b]

    if len(x_a) > 0 and len(x_b) > 0:
        d = get_sentence_distances(x_a, x_b)

        sents_a = [model.sents1[i] for i in sent_ids_a]
        sents_b = [model.sents2[i] for i in sent_ids_b]

        samples_a = [np.argsort(d[i])[::-1][:n_samples].tolist() for i in range(d.shape[0])]
        samples_b = [np.argsort(d[:, j])[::-1][:n_samples].tolist() for j in range(d.shape[1])]
    else:
        sents_a = []
        sents_b = []
        samples_a = []
        samples_b = []

    return sents_a, sents_b, samples_a, samples_b


def main():
    path_a = "../../data/corpus/hist-english/c1/ccoha1.txt"
    path_b = "../../data/corpus/hist-english/c2/ccoha2.txt"

    model = "../data/hist-english.pickle"

    targets = {"virus", "target", "hive", "plane_nn", "record_nn"}

    sents_a, sents_b = generate_sentence_samples(path_a, path_b, targets)

    print(sents_a.keys())

    print(sents_a["virus"][0:3])
    print(sents_b["virus"][0:3])

    print()

    print(sents_a["hive"][0:3])
    print(sents_b["hive"][0:3])


if __name__ == "__main__":
    main()
