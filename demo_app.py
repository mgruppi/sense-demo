from flask import Flask, render_template, request, jsonify
import os
import argparse
import numpy as np
import pickle
from scipy.spatial.distance import cosine
from sklearn.decomposition import PCA
import json
import html
from WordVectors import WordVectors
from preprocessing.generate_sentences import generate_sentence_samples
import re


app = Flask(__name__)
app.config["IMAGE_DIR"] = os.path.join("images")
data = {}


class Globals:
    def __init__(self):
        # wordvectors object for the first corpus
        self.wv1 = dict()
        # wordvectors object for the second corpus
        self.wv2 = dict()
        # list of words in common
        self.sorted_words = None
        self.distances_ab = dict()
        self.indices_ab = dict()
        self.distances_ba = dict()
        self.indices_ba = dict()
        self.d = dict()
        self.common = 0
        self.filename1 = "A"
        self.filename2 = "B"

        self.display_name = "Unnamed"
        self.common_vocab = 0
        self.description = "(description)"
        self.period_1 = (0, 0)
        self.period_2 = (1, 1)
        self.corpus_1 = "A"
        self.corpus_2 = "B"


def fetch_datasets(data_dir = "data"):
    """
    Returns a list of available datasets in `data`/
    """
    return [fstring.replace(".pickle", "") for fstring in os.listdir(data_dir)]


def fetch_metadata():
    """
    Returns a list of dictionaries containing the metadata for each dataset.
    """
    for root, dir, files in os.walk("metadata"):
        metadata = dict()
        for f in files:
            with open(os.path.join(root, f)) as fin:
                metadata[f.split(".")[0]] = json.load(fin)
    return metadata


@app.route("/", methods=["GET", "POST"])
def index():
    method = request.method

    if method == "GET":

        datasets = fetch_datasets()
        metadata = fetch_metadata()

        # Set up the data dict, initialize it with None
        for d in datasets:
            data[d] = None

        return render_template("demo.html", data=None,
                               datasets=datasets,
                               metadata=metadata)
    else:
        pass


def load_data_file(dataset):
    """
    Loads database for a given dataset name
    """

    path = os.path.join("data", dataset+".pickle")
    try:
        with open(path, "rb") as fin:
            global data
            data[dataset] = pickle.load(fin)
    except FileNotFoundError as e:
        print("File not found", e)

# not used in the demo itself
@app.route("/loadDataset", methods=["GET", "POST"])
def load_dataset():
    """
    Loads a dataset on the server-side application.
    """
    data_path = request.args.get('data', type=str)
    load_data_file(data_path)

    return "ok", 200

# not used in the demo itself
@app.route("/getMostShiftedWords", methods=["GET"])
def get_most_shifted():
    """
    Gets the most shifted words for a given alignment method from a loaded dataset.
    """

    if data is None:
        return "Error: dataset not loaded.", 400

    dataset = request.args.get("dataset", type=str)
    method = request.args.get("method", type=str)

    if data[dataset] is None:
        load_data_file(dataset)

    d_cosine = np.array([cosine(u, v)
                         for u, v in zip(data[dataset].wv1[method].vectors, data[dataset].wv2[method].vectors)])
    i_most_shifted = np.argsort(d_cosine)[::-1]  # Indices sorted by highest to lowers cosine distance
    n = 20

    out_words = [data[dataset].wv1[method].words[i] for i in i_most_shifted[:n]]
    out_scores = ["%.4f" % float(d_cosine[i]) for i in i_most_shifted[:n]]

    output = {"method": method, "words": out_words, "scores": out_scores}
    output = jsonify(output)

    return output, 200


def get_neighbor_coordinates(x):
    """
    Apply decomposition to an input matrix and returns a 2d set of points.
    """
    _x = PCA(n_components=2).fit_transform(x)

    return _x.tolist()


@app.route("/getWordContext", methods=["GET"])
def get_word_context():
    """
    Returns the nearest neighbors of a given target word in each of the input corpora.
    """

    if data is None:
        return "Error: dataset not loaded.", 400

    target = request.args.get("target", type=str)
    m = request.args.get("method", type=str)
    dataset = request.args.get("dataset", type=str)

    if data[dataset] is None:  # Dataset not loaded. Load it now.
        load_data_file(dataset)

    if m not in {"s4", "global", "noise-aware"}:
        m = "s4"

    if target not in data[dataset].wv1[m]:  # Word not found
        output = {"error": "word not found"}
    else:
        target_id = data[dataset].wv1[m].word_id[target]
        output = {"target": target}
        neighbor_ids_ab = data[dataset].indices_ab[m][target_id]
        neighbor_ids_ba = data[dataset].indices_ba[m][target_id]
        n_ab = [data[dataset].wv1[m].words[i] for i in neighbor_ids_ab]
        n_ba = [data[dataset].wv2[m].words[i] for i in neighbor_ids_ba]
        output["neighbors_ab"] = n_ab
        output["neighbors_ba"] = n_ba

        # Compute coordinates
        x_ab = get_neighbor_coordinates([data[dataset].wv1[m][target_id]] + [data[dataset].wv2[m][i]
                                                                             for i in neighbor_ids_ab])
        x_ba = get_neighbor_coordinates([data[dataset].wv2[m][target_id]] + [data[dataset].wv1[m][i]
                                                                             for i in neighbor_ids_ba])
        output["x_ab"] = x_ab
        output["x_ba"] = x_ba

    return jsonify(output), 200


def highlight_sentence(sent, target, tag_s="<span class='target-highlight'>", tag_e="</span>"):
    """
    Given an input sentence `sent` and a target word `target`, return a string that wraps every occurrence of `target`
    in `sent` with a tag for highlighting.
    By default, it surrounds every occurrence of `target` with the <span class='target-highlight'> tag.
    Args:
        sent (str): Input sentence.
        target (str): Target word to be highlighted.
        tag_s (str, optional): Sets the starting tag before `target`.
        tag_e (str, optional): Sets the ending tag after `target`.
    Return:
        sent_ (str): Output sentence.
    """

    # case insensitive sub, replaces original casing
    # sent_ = re.sub(target, "%s%s%s" % (tag_s, target, tag_e), sent, flags=re.IGNORECASE)

    # Case insensitive detection, case-preserving substitution.
    sent_ = html.escape(sent)
    sent_ = re.sub(r"(\W+|^)(%s)(\W+|$)" % target, r"\1%s\2%s\3" % (tag_s, tag_e), sent_, flags=re.IGNORECASE)
    return sent_


@app.route("/getWords", methods=["GET"])
def get_words():
    """
    Returns the list of wall words in the loaded data model.
    """

    if data is None:
        return "Error: dataset not loaded.", 400

    dataset = request.args.get("dataset", type=str)
    words = sorted(data[dataset].wv1["s4"].words)

    if data[dataset] is None:  # Dataset not loaded. Load it now.
        load_data_file(dataset)

    output = {"words": words}
    return jsonify(output), 200


@app.route("/getSentenceExamples", methods=["GET"])
def get_sentence_examples():
    """
    Returns sentence examples for a given word in different corpora A and B.
    """
    if data is None:
        return "Error: dataset not loaded.", 400

    target = request.args.get("target", type=str)
    m = request.args.get("method", type=str)
    dataset = request.args.get("dataset", type=str)

    if data[dataset] is None:  # Dataset not loaded. Load it now.
        load_data_file(dataset)

    if m not in {"s4", "global", "noise-aware"}:
        m = "s4"

    if target not in data[dataset].wv1["s4"]:
        return jsonify({"error": "word not found"}), 200

    sents_a, sents_b, samples_a, samples_b = generate_sentence_samples(data[dataset], target, method=m)

    # Highlight target words
    sents_a = [highlight_sentence(s, target) for s in sents_a]
    sents_b = [highlight_sentence(s, target) for s in sents_b]

    output = {"sents_a": sents_a, "sents_b": sents_b, "samples_a": samples_a, "samples_b": samples_b}
    return jsonify(output), 200


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host address of the app")
    parser.add_argument("--production", action="store_true", help="Run in production mode (debug off).")
    args = parser.parse_args()

    debug = not args.production
    app.run(host="0.0.0.0", debug=debug)
