import argparse
import sys
import pickle
import logging
import json
import uuid
from preprocessing.embedding import cleanup_corpus
from gensim.models import Word2Vec
from WordVectors import WordVectors
# 
WORD2VEC = "Word2Vec"
CORPORA_PREFIX = "preprocessing/generate_embeddings/corpora/"
TOKENIZATION_PREFIX = "preprocessing/generate_embeddings/tokenizations/"
TRAINED_MODEL_PREFIX = "preprocessing/generate_embeddings/models/trained/"
STATIC_MODEL_PREFIX = "preprocessing/generate_embeddings/models/pretrained/"
EMBEDDINGS_PREFIX = "preprocessing/generate_embeddings/embeddings/"

"""
[
{
corpus_id: uuid
corpus_name: str,
plaintext_path: str,
tokenizations: 
    [
        {
            tokenization_id: uuid,
            tokenization_name: str,
            tokenization_config:
                {
                <arbitrary config data>
                },
            tokenization_path: str,
            models: 
            [
                {
                model_id: uuid
                model_config: 
                    {
                    <arbitrary config data>
                    },
                model_path: str
                embeddings: 
                    [
                        {
                        embedding_id: uuid
                        embedding_config: 
                            {
                            <arbitrary config data>
                            }
                        embedding_path: 
                        }
                    ]
                }
            ]
        }
    ]
    ]

"""
def preprocess(lines, config):
    workers = config["workers"]
    sentences = cleanup_corpus(lines, workers)
    return sentences

def train_model(preprocessed_sentences: list[list[str]], model_type: str, model_config: dict):
    """
    preprocessed_sentences: list[list[str]] where each str is a token
    model_type: str representing the type of the model, for example "Word2Vec"
    model_config: dict[str, any] representing arbitrary configuration for the given model_type
    returns: trained model object
    """
    if model_type == WORD2VEC:
            trained_model = Word2Vec(sentences=preprocessed_sentences, **model_config)
            return trained_model
    else:
        print("ERROR: uknown model type")
        exit(1)

def embed(trained_model, model_type: str, preprocessed_sentences: list[list[str]], embedding_config: dict, save_path: str):
    """
    trained_model: w2vec model (or other) that has already been trained
    model_type: type of the model eg "Word2Vec"
    preprocessed_sentences: list[list[str]] where each str is a word to be embedded; each list[str] represents a sentence
    returns: None; it saves a WordVectors object representing an embedding to save_path
    """
    if model_type == WORD2VEC:
        wv = WordVectors(words=trained_model.wv.index_to_key, vectors=trained_model.wv.vectors)
        wv.save_txt(save_path)
    else:
        print(f"ERROR: attempted to perform embedding with unknown model type: {model_type}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("embeddings_config", type=str, help="path to embeddings configuration")
    args = parser.parse_args()
    # crawl the config and generate embeddings that don't yet exist
    with open(args.embeddings_config) as config_file:
        config = json.loads(config_file.read())
        for corpus in config:
            if "corpus_id" not in corpus:
                # we have a brand new corpus
                corpus["corpus_id"] = str(uuid.uuid4())
                print(f"Found new corpus: {corpus['corpus_name']}.")
                print(f"Assigned new corpus id as: {corpus['corpus_id']}.")
            else:
                print(f"Found corpus with id: {corpus['corpus_name']}.")
            with open(corpus["corpus_path"]) as plaintext:
                for tokenization in corpus["tokenizations"]:
                    if "tokenization_id" not in tokenization:
                        tokenization["tokenization_id"] = str(uuid.uuid4())
                        print(f"Found new tokenization for {corpus['corpus_name']}:{tokenization['tokenization_name']}.")
                        print(f"Assigned new tokenization id as: {tokenization['tokenization_id']}.")
                        # do the tokenization and save it to disk
                        tokenization_path = TOKENIZATION_PREFIX + tokenization["tokenization_id"] + ".pickle"
                        tokenization["tokenization_path"] = tokenization_path 
                        print(f"Performing tokenization for {corpus['corpus_name']}:{tokenization['tokenization_name']}.")
                        tokenized = preprocess(plaintext.readlines(), tokenization["tokenization_config"])
                        print(f"Writing tokenization to disk as {tokenization_path}")
                        with open(tokenization_path, "wb") as tokenization_file:
                            pickle.dump(tokenized, tokenization_file)
                    else:
                        # todo: avoid reading tokenized in this case if we don't have to generate a new model. this will not happen frequently
                        # ie precheck the models for each tokenization and see if they need to be generated
                        print(f"Found existing tokenization for {corpus['corpus_name']}:{tokenization['tokenization_name']}. Will load from disk if needed.")
                        with open(tokenization["tokenization_path"], "rb") as tokenization_file:
                            tokenized = pickle.load(tokenization_file)
                    for model in tokenization["models"]:
                        # todo: this part isn't great and probably has bugs
                        if "model_id" not in model and model["train_on_corpus"]:
                            # we have a brand new model to make
                            model["model_id"] = str(uuid.uuid4())
                            print(f"Found new model to train for {corpus['corpus_name']}:{tokenization['tokenization_name']}:{model['model_name']}.")
                            print(f"Wrote new model id as: {model['model_id']}.")

                            model_path = TRAINED_MODEL_PREFIX + model["model_id"] + ".pickle"
                            model["model_path"] = model_path
                            model_to_use = train_model(tokenized, model["model_type"], model["model_config"])
                            with open(model_path, "wb") as output_file:
                                pickle.dump(model_to_use, output_file)

                        else:
                                
                            # check the model type and set the model_path to the static model
                            print(f"Found existing model for {corpus['corpus_name']}:{tokenization['tokenization_name']}:{model['model_name']}. Will load from disk if needed.")
                            with open(model["model_path"], "rb") as model_file:
                                model_to_use = pickle.load(model_file)
                        for embedding in model["embeddings"]:
                            if "embedding_id" not in embedding:
                                # we have a brand new embedding
                                embedding["embedding_id"] = str(uuid.uuid4())
                                print(f"Found new embedding to generate for {corpus['corpus_name']}:{tokenization['tokenization_name']}:{model['model_name']}:{embedding['embedding_name']}")
                                print(f"Assigned new embedding id as: {embedding['embedding_id']}.")

                                embedding_path = EMBEDDINGS_PREFIX + model["model_id"] + ".txt"
                                generated_embedding = embed(model_to_use, model["model_type"], tokenized, embedding["embedding_config"], embedding_path)
                            else:
                                # todo: integrity check - confirm the embedding file actually exists
                                print(f"Embedding already exists for {corpus['corpus_name']}:{tokenization['tokenization_name']}:{model['model_name']}:{embedding['embedding_name']}. No action taken.")
                                pass
    # if we successfully generated all the embeddings, overwrite the config file
    print("Successfully generated all embeddings specified by config, overwriting config with any new data")
    with open(args.embeddings_config, "w") as config_file:
        json.dump(config, config_file, indent=2)

                     


        
        

