#/bin/bash

in_path="../../s4/corpus"
out_path="../../s4/embeddings"
datasets=(hist-english hist-german hist-latin hist-swedish ukus)


for f in ${datasets[@]}
do
  mkdir -p "$out_path/$f"
  echo "$f"
  for g in $in_path/$f/c1/*
  do
    python3 embedding.py "$g" "$out_path/$f/c1.vec"
  done
  for g in $in_path/$f/c2/*
  do
    python3 embedding.py "$g" "$out_path/$f/c2.vec"
  done
done