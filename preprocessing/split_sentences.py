"""
Split sentences into sequences of at most N tokens
"""
import os
import re


path = "/data/gouvem/s4/corpus/arxiv-ai-phys/sentences/"

files = os.listdir(path)

for f in files:
    sentences = set()
    step = 20
    with open(os.path.join(path, f)) as fin:
        lines = "\n".join(fin.readlines())
    r = re.compile(r"\s+|\n+")
    tokens = r.split(lines)

    for i in range(0, len(tokens), step):
        sent = tuple(tokens[i:i+step])
        sentences.add(sent)

    with open(f, "w") as fout:
        for sent in sentences:
            fout.write("%s\n" % " ".join(sent))



