#!/bin/bash

# Executes the full preprocessing pipeline for the demo on a given pair of corpus.
#   1 - Trains word embeddings on each corpus A and B
#   2 - Aligns the resulting embedding using each alignment method
#   3 - Pre-compute the nearest neighbors for each alignment method
#   4 - Preprocess the sentence examples

in_path_emb="../s4/corpus"
out_path_emb="../s4/embeddings"
datasets=(hist-english hist-german hist-latin hist-swedish ukus)

#w2v params
vector_size=100
window=10
min_count=50

for f in ${datasets[@]}
do
  echo "Training embeddings for $f"
  mkdir -p "$out_path_emb/$f"
  echo "$f"
  for g in $in_path_emb/$f/c1/*
  do
    python3 -m preprocessing.embedding "$g" "$out_path_emb/$f/c1.vec" \
      --vector_size="$vector_size" \
      --window="$window" \
      --min_count="$min_count"
  done
  for g in $in_path_emb/$f/c2/*
  do
    python3 -m preprocessing.embedding "$g" "$out_path_emb/$f/c2.vec" \
      --vector_size="$vector_size" \
      --window="$window" \
      --min_count="$min_count"
  done
done


for d in ${datasets[@]}
do
  echo "Generating examples for $d"
  python3 -m preprocessing.generate_examples \
          "$root/$d/c1.vec" \
          "$root/$d/c2.vec" \
          "$sentences/$d/sentences/c1.txt" \
          "$sentences/$d/sentences/c2.txt" \
          "data/$d.pickle"
done