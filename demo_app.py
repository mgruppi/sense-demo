from flask import Flask, render_template, request, jsonify
import os
import argparse
import numpy as np
import re
import pickle
from scipy.spatial.distance import cosine
from noise_aware import noise_aware

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


@app.route("/", methods=["GET", "POST"])
def index():
    method = request.method
    
    if method == "GET":
        return render_template("demo.html", data=None)
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

    print(data.wv1.keys())

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
    n = 20

    out_words = [data.wv1[method].words[i] for i in i_most_shifted[:n]]
    out_scores = ["%.4f" % float(d_cosine[i]) for i in i_most_shifted[:n]]

    output = {"words": out_words, "scores": out_scores}
    output = jsonify(output)

    return output, 200


debug = not args.production
app.run(host="0.0.0.0", debug=debug)
