from generate_examples import generate_sentence_samples, Globals

path_a = "../../data/corpus/hist-english/c1/ccoha1.txt"
path_b = "../../data/corpus/hist-english/c2/ccoha2.txt"

model = "../data/hist-english.pickle"

targets = {"virus", "target", "hive", "plane_nn", "record_nn"}

sents_a, sents_b = generate_sentence_samples(model, path_a, path_b, targets)

print(sents_a.keys())


print(sents_a["virus"][0:3])
print(sents_b["virus"][0:3])

print()

print(sents_a["hive"][0:3])
print(sents_b["hive"][0:3])
