from flask import Flask, render_template, request
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


@app.route("/", methods=["GET", "POST"])
def index():
    method = request.method
    
    if method == "GET":
        return render_template("demo.html", data=None)
    else:
        pass


debug = not args.production
app.run(host="0.0.0.0", debug=debug)
