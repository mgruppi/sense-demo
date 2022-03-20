from flask import Flask, render_template, request, jsonify
import os
import argparse
import numpy as np
import pickle
from scipy.spatial.distance import cosine
from sklearn.decomposition import PCA
import json
import html
from app.preprocessing.WordVectors import WordVectors
from preprocessing.generate_sentences import generate_sentence_samples
import re

# load app constants from file
with open("metadata/application_constants.json") as constants_file:
    app_constants = json.loads(constants_file.read())
# variable to hold the example we are currently serving to the user
current_example = None
def load_example(example_id):
    """
    example_id: id of an example to load from disk
    returns: None, has the side effect of loading an example from disk for future API calls
    """
    # todo don't add paths like this because it's not os-agnostic
    examples_prefix = app_constants["EXAMPLES_PREFIX"]
    example_path = examples_prefix + example_id + ".pickle"
    with open(example_path, "rb") as ex:
        global current_example
        current_example = pickle.load(ex)

def fetch_datasets():
    """
    open the metadata file for all the examples
    this file contains data that gets passed to the template to be used in the dataset selection screen
    returns: dictionary with strings as keys
    guaranteed to have the following key/value pairs:
    "display_name": str 
    "corpus_1_display_name": str
    "corpus_2_display_name": str
    "description": str
    "embedding_a_id": str
    "embedding_b_id": str
    "alignments":list[dict[str, str]]
    and each dict within alignments is guaranteed to have keys
    "name", "generated_already"
     """
    with open(app_constants["EXAMPLES_CONFIG"]) as examples_config_file:
        examples_config = json.loads(examples_config_file.read())
    return examples_config 
app = Flask(__name__)
app.config["IMAGE_DIR"] = os.path.join("images")
@app.route("/")
def index():
    datasets_metadata = fetch_datasets()
    return render_template("layout.html", datasets_metadata=datasets_metadata)

@app.route("/loadDataset")
def load_dataset():
    """
    Loads a dataset on the server-side application.
    """
    initial_load = request.args.get("initial_load", type=bool)
    if initial_load:
        # we are loading a dataset on application load
        datasets = fetch_datasets()
        for dataset in datasets:
            if "example_id" in dataset:
                example_id = dataset["example_id"]
                load_example(example_id)
                return example_id, 200
        err_out = "Server couldn't find a dataset in the examples metadata file with an id on initial load"
        return err_out, 500
    else: 
        example_id = request.args.get('id', type=str)
        load_example(example_id)
        return example_id, 200


@app.route("/getMostShiftedWords", methods=["GET"])
def get_most_shifted():
    """
    Gets the most shifted words for a given alignment method from a loaded dataset.
    """
    dataset_id = request.args.get("id", type=str)
    method = request.args.get("alignment_type", type=str)
    # DO IT LIVE HERE if we get an alignment our dataset doens't have

    if current_example is None:
        load_example(dataset_id)
    # todo query current_example for this data
    out_words = ["hello","world"]
    out_scores = ["0.1, 0.2"]
    output = {"method": method, "words": out_words, "scores": out_scores}
    output = jsonify(output)
    return output, 200



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
