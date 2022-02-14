import argparse
import pickle
import logging
import json
import uuid
from gensim.models import Word2Vec
import WordVectors
from Tokenizer import tokenize_with_config
WORD2VEC = "Word2Vec"
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
def train_model(tokenized_sentences: list[list[str]], model_type: str, model_config: dict, save_path: str):
    """
    tokenized_sentences: list[list[str]] where each str is a token
    model_config: dict[str, any] representing arbitrary configuration for the model
    """
    if model_type == WORD2VEC:
            trained_model = Word2Vec(sentences=tokenized_sentences, **model["model_config"])
            with open(save_path, "wb") as output_file:
                pickle.dump(trained_model, output_file)
            return trained_model
    else:
        print("ERROR: uknown model type")
        exit(1)
def embed(trained_model, model_type: str, tokenized_sentences: list[list[str]], embedding_config: dict, save_path: str):
    if model_type == WORD2VEC:
        wv = WordVectors(words=model.wv.index_to_key, vectors=model.wv.vectors)
        wv.save_txt(save_path)

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
                corpus["corpus_id"] = uuid.uuid4()
                logging.info(f"Found new corpus: {corpus['corpus_name']}.")
                logging.info(f"Wrote new corpus id as: {corpus['corpus_id']}.")
            else:
                logging.info(f"Found existing corpus: {corpus['corpus_name']}.")
            with open(corpus["plaintext_path"]) as plaintext:
                for tokenization in corpus["tokenizations"]:
                    if "tokenization_id" not in tokenization:
                        tokenization["tokenization_id"] = uuid.uuid4()
                        logging.info(f"Found new tokenization for {corpus['corpus_name']}:{tokenization['tokenization_name']}.")
                        logging.info(f"Wrote new tokenization id as: {tokenization['tokenization_id']}.")
                        # do the tokenization and save it to disk
                        tokenization_path = "tokenizations" + tokenization["tokenization_id"] + ".pickle"
                        tokenization["tokenization_path"] = tokenization_path 
                        logging.info(f"Performing tokenization for {corpus['corpus_name']}:{tokenization['tokenization_name']}.")
                        tokenized = tokenize_with_config(plaintext.readlines(), tokenization["tokenization_config"])
                        logging.info(f"Writing tokenization to disk as {tokenization_path}")
                        pickle.dump(tokenized, tokenization_path)
                    else:
                        # todo: avoid reading tokenized in this case if we don't have to generate a new model
                        # ie precheck the models for each tokenization and see if they need to be generated
                        logging.info(f"Found existing tokenization for {corpus['corpus_name']}:{tokenization['tokenization_name']}. Loading from disk.")
                        tokenized = pickle.load(tokenization["tokenization_path"])
                    for model in tokenization["models"]:
                        if "model_id" not in model:
                            # we have a brand new model to make
                            model["model_id"] = uuid.uuid4()
                            logging.info(f"Found new model to train for {corpus['corpus_name']}:{tokenization['tokenization_name']}:{model['model_name']}.")
                            logging.info(f"Wrote new model id as: {tokenization['model_id']}.")
                            if model["train_on_corpus"]:
                                # if this is a model type that we train on the corpus (like w2vec), train it
                                model_path = "models" + model["model_id"] + ".pickle"
                                model["model_path"] = model_path
                                trained_model = train_model(tokenized, model["model_type"], model["model_config"], model_path)
                            else:
                                # check the model type and set the model_path to the static model
                                trained_model = pickle.load(model["model_path"])
                        for embedding in model["embeddings"]:
                            if "embedding_id" not in embedding:
                                # we have a brand new embedding
                                embedding["embedding_id"] = uuid.uuid4()
                                embedding_path = "models" + model["model_id"] + ".pickle"

                                generated_embedding = embed(trained_model, tokenized, embedding_config, save_path)
                            else:
                                # integrity check - confirm the embedding file actually exists
                                pass








                     


        
        

