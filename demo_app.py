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

# load app constants from file
with open("metadata/application_constants.json") as constants_file:
    app_constants = json.loads(constants_file.read())

def fetch_datasets():
    with open(app_constants["EXAMPLES_CONFIG"]) as examples_config_file:
        examples_config = json.loads(examples_config_file.read())
    return 

app = Flask(__name__)
app.config["IMAGE_DIR"] = os.path.join("images")
@app.route("/")
def index():
    datasets_metadata = fetch_datasets()
    return render_template("layout.html", datasets_metadata=datasets_metadata)


def get_neighbor_coordinates(x):
    """
    Apply decomposition to an input matrix and returns a 2d set of points.
    """
    _x = PCA(n_components=2).fit_transform(x)

    return _x.tolist()


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

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host address of the app")
    parser.add_argument("--production", action="store_true", help="Run in production mode (debug off).")
    args = parser.parse_args()

    debug = not args.production
    app.run(host="0.0.0.0", debug=debug)
