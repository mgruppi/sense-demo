import pickle
from preprocessing.WordVectors import WordVectors


path_in = input("Path to input model: ")

with open(path_in, "rb") as fin:
    data = pickle.load(fin)

print(dir(data))

while True:
    expr = input("Enter expression ")
    eval(expr)

