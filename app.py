from flask import Flask, render_template, request
import os
import numpy as np
import re
import pickle

from WordVectors import WordVectors, intersection
from scipy.spatial.distance import cosine
from alignment import align
from mapping import perform_mapping
from noise_aware import noise_aware
from generate_examples import Globals
import s4
import globals
import plot

app = Flask(__name__)
app.config["IMAGE_FOLDER"] = os.path.join("static", "image")

g = Globals()


def distribution_of_change(*wvs, metric="euclidean"):
    """
    Gets distribution of change per word across input WordVectors list wvs.
    Assumes the WordVectors in wvs have been previously aligned to the same reference point
    (E.g.: align all to wvs[0]).
    Arguments:
            wvs - list of WordVectors objects
    Returns:
            d   - array of N elements with the mean cosine distance across the aligned WordVectors
                    (N is the size of the common vocabulary)
    """

    d = np.zeros((len(wvs[0])))
    for i, w in enumerate(wvs[0].words):
        # Compute mean vector
        v_mean = np.mean([wv[w] for wv in wvs], axis=0)
        # Compute distances to the mean
        if metric == "euclidean":
            distances = [np.linalg.norm(v_mean-wv[w])**2 for wv in wvs]
        elif metric == "cosine":
            distances = [cosine(v_mean, wv[w]) for wv in wvs]
        # distances = [cosine(v_mean, wv[w]) for wv in wvs]
        mean_d = np.mean(distances)
        d[i] = mean_d
    return d


def read_string(s):
    # Use this function to process line reading in map
    def process_line(s):
        s = s.rstrip().split(b' ', 1)
        w = s[0]
        v = np.array(s[1].split(b' '), dtype=float)
        return w.decode("utf-8"), v

    lines = s.strip().split(b'\n')
    lines = lines[1:]
    data = map(process_line, lines)
    words, vectors = zip(*data)
    return words, vectors


@app.route('/', methods=["POST", "GET"])
def index():
    method = request.method
    print(method)

    if method == "GET":
        return render_template("demo_old.html",
        data=None
        )
    else:

        # Skip for now, pre-made examples
        # print("FILES", request.files)
        # print(request.files["input1"])
        # print(request.files["input2"])

        example = request.form.get("examples")
        global g
        if example == "ukus":
            fpath = "ukus.pickle"
        elif example == "hist-eng":
            fpath = "hist-eng.pickle"
        elif example == "arxiv-ai-phys":
            fpath = "arxiv-ai-phys.pickle"
        elif example == "news":
            fpath = "news.pickle"
        elif example == "german":
            fpath = "german.pickle"

        fpath = os.path.join("data", fpath)
        with open(fpath, "rb") as fin:
            g = pickle.load(fin)

        methods = set(request.form.getlist("align"))
        print(methods)

        # f1 = request.files["input1"].read()
        # words, vectors = read_string(f1)
        #
        # wv1 = WordVectors(words=words, vectors=vectors)
        #
        # f2 = request.files["input2"].read()
        # words, vectors = read_string(f2)
        # wv2 = WordVectors(words=words, vectors=vectors)
        #
        # wv1, wv2 = intersection(wv1, wv2)
        #
        # if "global" in methods:
        #     # Use global anchors
        #     g.wv1["global"], g.wv2["global"], _ = align(wv1, wv2)
        #     words = wv1.words
        #     g.sorted_words = sorted(words)
        #     g.distances["global"], g.indices["global"] = perform_mapping(g.wv1["global"],
        #                                                                             g.wv2["global"])
        # if "s4" in methods:
        #     # Get s4 anchors
        #     anchors, non_anchors, _ = s4.s4(wv1, wv2, verbose=1, iters=100)
        #     g.wv1["s4"], g.wv2["s4"], _ = align(wv1, wv2, anchor_words=anchors)
        #     # Mapping
        #     g.distances["s4"], g.indices["s4"] = perform_mapping(g.wv1["s4"], g.wv2["s4"])
        #
        # if "noise-aware" in methods:
        #     # Get noise-aware anchors
        #     _, alpha, anchors, non_anchors = noise_aware(wv1.vectors, wv2.vectors)
        #     g.wv1["noise-aware"], g.wv2["noise-aware"], _ = align(wv1, wv2, anchor_words=anchors)
        #     g.distances["noise-aware"], g.indices["noise-aware"] = \
        #         perform_mapping(g.wv1["noise-aware"], g.wv2["noise-aware"])

        # print("Finished reading")
        # print(len(words), "words")

        words = g.wv1["global"].words
        top_words = dict()

        for m in methods:
            d = distribution_of_change(g.wv1[m], g.wv2[m], metric="cosine")
            words_sorted = np.argsort(d)[::-1]
            top_w = [words[i] for i in words_sorted[:40]]
            top_words[m] = top_w

        # top_words = [words[i] for i in words_sorted[:40]]
        # distances = {words[i]: "%.4f" % d[i] for i in words_sorted[:40]}

        img_path = os.path.join(app.config["IMAGE_FOLDER"], "tmp.png")
        plot.plot_words(g.wv1["global"], g.wv2["global"], top_words["global"][:10], img_path)

        # Store result data
        data = dict()
        data["common"] = g.common
        data["filename1"] = g.filename1
        data["filename2"] = g.filename2
        # data["common"] = len(words)
        # data["filename1"] = request.files["input1"].filename
        # data["filename2"] = request.files["input2"].filename

        return render_template("demo_old.html", data=data,
                                img=img_path,
                                words=top_words,
                                distances=None)


@app.route("/query", methods=["GET"])
def query_suggestion():
    """
        Returns real-time suggestions of words when querying
        TODO: Use Trie for efficient search
    """

    if g.sorted_words is None:
        return "No suggestions"
    q_arg = request.args.get("q").lower()

    hint = ""  # holds the HTML for hint
    regex = re.compile(q_arg)
    limit = 10  # limits number of suggestions
    count = 0  # count suggestions
    for word in g.sorted_words:
        if count >= limit:
            break
        match = regex.match(word)
        if match:
            count += 1
            if hint == "":
                hint = "<a href='#' onclick=loadQuery(%s)> %s </a>" % (word, word)
            else:
                hint = hint + "<br /> <a href='#' onclick=loadQuery(%s)> %s </a>" % (word, word)

    if hint == "":
        return "No suggestions"
    else:
        return hint


@app.route("/mapping", methods=["GET"])
def get_mapping():
    """
        Returns mapping of argument word
    """
    if g.wv1 is None or g.wv2 is None:
        return ""
    elif g.distances_ab is None or g.indices_ab is None:
        return ""

    q_arg = request.args.get("q")

    if q_arg not in g.sorted_words:
        return "Invalid word"

    q_arg = q_arg.lower()
    print("***", q_arg)

    # Stores output as a mapping of method->result
    # Each result is a mapping of word->distance
    output = dict()
    output["ab"] = dict()
    output["ba"] = dict()
    for method in g.wv1:
        word_id = g.wv1[method].word_id[q_arg]
        output["ab"][method] = {g.wv1[method].words[i]: "%.4f" % j for i, j in zip(g.indices_ab[method][word_id],
                                                                                   g.distances_ab[method][word_id])}
        output["ba"][method] = {g.wv1[method].words[i]: "%.4f" % j for i, j in zip(g.indices_ba[method][word_id],
                                                                                   g.distances_ba[method][word_id])}
    return output


app.run(host="0.0.0.0", debug=True)
