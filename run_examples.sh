#!/bin/bash
root="../s4/wordvectors"

mkdir "data"

pairs=("$root/arxiv/arXiv_category_cs.AI.vec $root/arxiv/arXiv_category_physics.class-ph.vec data/ai-phys.pickle"
      "$root/arxiv/arXiv_category_cs.AI.vec $root/arxiv/arXiv_category_physics.atom-ph.vec data/ai-atom-ph.pickle"
      "$root/arxiv/arXiv_category_cs.AI.vec $root/arxiv/arXiv_category_cond-mat.mtrl-sci.vec data/ai-mtrl-sci.pickle"
      "$root/semeval/english-corpus1.vec $root/semeval/english-corpus2.vec data/semeval-english.pickle"
      "$root/semeval/german-corpus1.vec $root/semeval/german-corpus2.vec data/semeval-german.pickle"
      "$root/semeval/latin-corpus1.vec $root/semeval/latin-corpus2.vec data/semeval-latin.pickle"
      "$root/semeval/swedish-corpus1.vec $root/semeval/swedish-corpus2.vec data/semeval-swedish.pickle"
      "$root/ukus/bnc.vec $root/ukus/coca.vec data/uk-us.pickle"
      )
for p in "${pairs[@]}"
do
  echo $p
  python3 generate_examples.py "$p"
done;