from flask import Flask, render_template, request, jsonify
import os
import argparse
import numpy as np
import pickle
from scipy.spatial.distance import cosine
from sklearn.decomposition import PCA
import json

parser = argparse.ArgumentParser()
parser.add_argument("--host", type=str, default="0.0.0.0", help="Host address of the app")
# parser.add_argument("--debug", action="store_true", help="Set debug mode to ON")
parser.add_argument("--production", action="store_true", help="Run in production mode (debug off).")
args = parser.parse_args()

app = Flask(__name__)
app.config["IMAGE_DIR"] = os.path.join("images")

data = None


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

        self.display_name = "Unnamed"
        self.common_vocab = 0
        self.description = "(description)"
        self.period_1 = (0, 0)
        self.period_2 = (1, 1)
        self.corpus_1 = "A"
        self.corpus_2 = "B"


def fetch_datasets():
    """
    Returns a list of available datasets in `data`/
    """
    for root, dir, files in os.walk("data"):
        datasets = [f.replace(".pickle", "") for f in files]
    return datasets


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
        return render_template("demo.html", data=None,
                               datasets=datasets,
                               metadata=metadata)
    else:
        pass


@app.route("/loadDataset", methods=["GET", "POST"])
def load_dataset():
    """
    Loads a dataset on the server-side application.
    """
    data_path = request.args.get('data', type=str)
    path = os.path.join("data", data_path+".pickle")

    with open(path, "rb") as fin:
        global data
        data = pickle.load(fin)

    return "ok", 200


@app.route("/getMostShiftedWords", methods=["GET"])
def get_most_shifted():
    """
    Gets the most shifted words for a given alignment method from a loaded dataset.
    """

    if data is None:
        return "Error: dataset not loaded.", 400

    method = request.args.get("method", type=str)

    d_cosine = np.array([cosine(u, v) for u, v in zip(data.wv1[method].vectors, data.wv2[method].vectors)])
    i_most_shifted = np.argsort(d_cosine)[::-1]  # Indices sorted by highest to lowers cosine distance
    n = 10

    out_words = [data.wv1[method].words[i] for i in i_most_shifted[:n]]
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
    m = "global"

    if target not in data.wv1[m]:  # Word not found
        output = {}
    else:
        target_id = data.wv1[m].word_id[target]
        output = {"target": target}
        neighbor_ids_ab = data.indices_ab[m][target_id]
        neighbor_ids_ba = data.indices_ba[m][target_id]
        n_ab = [data.wv1[m].words[i] for i in neighbor_ids_ab]
        n_ba = [data.wv2[m].words[i] for i in neighbor_ids_ba]
        output["neighbors_ab"] = n_ab
        output["neighbors_ba"] = n_ba

        # Compute coordinates
        x_ab = get_neighbor_coordinates([data.wv1[m][target_id]] + [data.wv2[m][i] for i in neighbor_ids_ab])
        x_ba = get_neighbor_coordinates([data.wv2[m][target_id]] + [data.wv1[m][i] for i in neighbor_ids_ba])
        output["x_ab"] = x_ab
        output["x_ba"] = x_ba

    return jsonify(output), 200


debug = not args.production
app.run(host="0.0.0.0", debug=debug)
