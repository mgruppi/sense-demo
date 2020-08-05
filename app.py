from flask import Flask, render_template, request
import json
import os
import numpy as np
from datetime import datetime
import requests
from requests.auth import HTTPBasicAuth

from WordVectors import WordVectors, intersection
from alignment import align
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

        wv1 = WordVectors(words=words, vectors=vectors)

        f2 = request.files["input2"].read()
        words, vectors = read_string(f2)
        wv2 = WordVectors(words=words, vectors=vectors)

        wv1, wv2 = intersection(wv1, wv2)
        wv1, wv2, _ = align(wv1, wv2)
        words = wv1.words
        print("Finished reading")
        print(len(wv1), "words")


        d = distribution_of_change(wv1, wv2)
        words_sorted = np.argsort(d)[::-1]

        top_words = [words[i] for i in words_sorted[:40]]

        img_path = os.path.join(app.config["IMAGE_FOLDER"], "tmp.png")
        plot.plot_words(wv1, wv2, top_words[:10], img_path)

        # Store result data
        data = dict()
        data["common"] = len(wv1)
        data["filename1"] = request.files["input1"].filename
        data["filename2"] = request.files["input2"].filename

        return render_template("demo.html", data=data,
                                img=img_path,
                                words=top_words)



# @app.route("/bnet", methods=["POST"])
# def bnet():
#     headers = request.headers
#     print(request.headers)
#     if not "auth" in headers:
#         print("Missing auth token")
#         return "HTTP/1.0 Unauthorized\n", 401
#     elif headers["auth"] != "4StbgT3q7b":
#         print("Invalid credentials")
#         return "HTTP/1.0 Unauthorized - Invalid credentials\n", 401
#
#     payload = {"grant_type": "client_credentials"}
#     response = requests.post("https://us.battle.net/oauth/token", data=payload,
#                 auth=("52881a8e401348cabcd9bc4d923194b7", "Rm7NscCvgdzEDWgGyji0oC6wnECU0Sjb"))
#
#     if response.status_code == 200:
#         data = json.loads(response.content)
#         token = data["access_token"]
#         print(token)
#         return token
#     else:
#         print(response)
#
#
# @app.route("/send", methods=["POST"])
# def send_data():
#     default_name = '0'
#     headers = request.headers
#
#     if not "auth-token" in headers:
#         print("Missing auth token")
#         return "HTTP/1.0 Unauthorized - Authentication needed", 401
#     elif headers["auth-token"] != AUTH_KEY:
#         print("Invalid credentials")
#         return "HTTP/1.0 Unauthorized - Invalid credentials", 401
#
#     data = dict(request.json)
#
#     print("%s -- received data" % datetime.now())
#
#     if not "name" in data:
#         return "HTTP/1.0 400 Bad Request -- Missing name field", 400
#
#
#     # Split display string into list
#     # if "display" in data:
#     #     data["display"] = data["display"].split(",")
#     # else:
#     #     data["display"] = [field for field in data if field not in ["Title", "name"]]
#     if not "display" in data:
#         data['display'] = [field for field in data if field not in {"Title", "name", "type"}]
#
#
#     if not os.path.exists("data/"):
#         os.mkdir("data/")
#
#     with open("data/"+data["name"]+".json", "w") as fout:
#         json.dump(data, fout)
#
#     return "HTTP/1.0 200 Created", 200

app.run(host="0.0.0.0", debug=True)
