from generate_examples import generate_sentence_samples, Globals

path_a = "../../data/corpus/hist-english/c1/ccoha1.txt"
path_b = "../../data/corpus/hist-english/c2/ccoha2.txt"

model = "../data/hist-english.pickle"

targets = {"plane_nn", "record_nn"}

generate_sentence_samples(model, path_a, path_b, targets)

