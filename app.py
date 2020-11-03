from flask import Flask, render_template, request
import os
import numpy as np
import re

from WordVectors import WordVectors, intersection
from scipy.spatial.distance import cosine
from alignment import align
from mapping import perform_mapping
import globals
import plot

app = Flask(__name__)
app.config["IMAGE_FOLDER"] = os.path.join("static", "image")


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
        return render_template("demo.html",
        data=None
        )
    else:
        print("FILES", request.files)
        print(request.files["input1"])
        print(request.files["input2"])

        f1 = request.files["input1"].read()
        words, vectors = read_string(f1)

        globals.wv1 = WordVectors(words=words, vectors=vectors)

        f2 = request.files["input2"].read()
        words, vectors = read_string(f2)
        globals.wv2 = WordVectors(words=words, vectors=vectors)

        globals.wv1, globals.wv2 = intersection(globals.wv1, globals.wv2)
        globals.wv1, globals.wv2, _ = align(globals.wv1, globals.wv2)
        words = globals.wv1.words
        globals.sorted_words = sorted(words)
        print("Finished reading")
        print(len(globals.wv1), "words")

        # Mapping
        globals.distances, globals.indices = perform_mapping(globals.wv1, globals.wv2)

        d = distribution_of_change(globals.wv1, globals.wv2)
        words_sorted = np.argsort(d)[::-1]

        top_words = [words[i] for i in words_sorted[:40]]

        img_path = os.path.join(app.config["IMAGE_FOLDER"], "tmp.png")
        plot.plot_words(globals.wv1, globals.wv2, top_words[:10], img_path)

        # Store result data
        data = dict()
        data["common"] = len(globals.wv1)
        data["filename1"] = request.files["input1"].filename
        data["filename2"] = request.files["input2"].filename

        return render_template("demo.html", data=data,
                                img=img_path,
                                words=top_words)


@app.route("/query", methods=["GET"])
def query_suggestion():
    """
        Returns real-time suggestions of words when querying
        TODO: Use Trie for efficient search
    """

    if globals.sorted_words is None:
        return "No suggestions"
    q_arg = request.args.get("q").lower()

    hint = ""  # holds the HTML for hint
    regex = re.compile(q_arg)
    for word in globals.sorted_words:
        match = regex.match(word)
        if match:
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
    if globals.wv1 is None or globals.wv2 is None:
        return []
    elif globals.distances is None or globals.indices is None:
        return []

    q_arg = request.args.get("q").lower()

    if q_arg not in globals.wv.word_id:
        return []

    word_id = globals.wv1.word_id[q_arg]
    output = list()
    for i in range(len(globals.distances[word_id])):
        output.append((globals.distances[word_id][i], globals.indices[word_id][i]))

    return output


app.run(host="0.0.0.0", debug=True)
