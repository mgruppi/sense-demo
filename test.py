import pickle
from demo_app import Globals  # import class to main module
path = "/home/brianhotopp/Dropbox/Spring 2022/Research/sense-demo/data/hist-english.pickle"
with open(path, "rb") as fin:
    dataset = pickle.load(fin)
#print(f"wv1: {dataset.wv1}")
#print(f"wv2: {dataset.wv2}")
#print(f"sorted_words: {dataset.sorted_words}")
#print(f"num words: {len(dataset.sorted_words)}")
print(f"distances_ab {dataset.distances_ab}")
print(f"len_distances: {len(dataset.distances_ab['global'])}")
#print(f"{dataset.indices_ab['global']}")
#print(f"{dataset.wv1.words[0]}")
#print(f"{dataset.wv2.words[0]}")

