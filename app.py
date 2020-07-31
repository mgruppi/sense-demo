from flask import Flask, render_template, request
import json
import os
from datetime import datetime
import requests
from requests.auth import HTTPBasicAuth
app = Flask(__name__)

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

        print(request.files["input1"].read())
        return render_template("demo.html", data=None)



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
