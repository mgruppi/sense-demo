import argparse
import pickle
import json
import uuid
from ..embedding import cleanup_corpus
from gensim.models import Word2Vec
from ..WordVectors import WordVectors
from nltk.tokenize import sent_tokenize, word_tokenize
import spacy

def preprocess(lines, config):
    workers = config["workers"]
    sentences = cleanup_corpus(lines, workers)
    return sentences
def set_model(preprocessed_sentences, model_config: dict, WORD2VEC):

    """
    preprocessed_sentences: list[list[str]] where each string is a token OR None, in the case that we are using a prebuilt model that doesn't need the sentences to train on
    model_config: dict[str, any] representing arbitrary configuration for the model to generate
    this dictionary is guaranteed to have a {"model_type", str} pair that tells us the type of model we are to return (model_type also tells us if we need to train on the given preprocessed_sentences)
    returns: trained model object (some model type enumerated in TRAINABLE_MODELS)
    """
    if model_config["model_type"] == WORD2VEC:
            # strip unused key, value pairs from config dictionary before passing the config_dict to the word2vec library function
            passthrough_dictionary = dict()
            for (key, value) in model_config.items():
                if key != "model_type":
                    passthrough_dictionary[key] = value
            trained_model = Word2Vec(sentences=preprocessed_sentences, **passthrough_dictionary)
            return trained_model
    else:
        print("ERROR: uknown model type")
        exit(1)

def embed(trained_model, model_config: dict, preprocessed_sentences: list[list[str]], embedding_config: dict, save_path: str, WORD2VEC):
    """
    trained_model: w2vec model (or other) that has already been trained
    model_config: configuration used to train/load the model, guaranteed to have key, value pair of {"model_type", str}
    preprocessed_sentences: list[list[str]] where each str is a word to be embedded; each list[str] represents a sentence
    returns: None; it saves a WordVectors object representing an embedding to save_path
    """
    model_type = model_config["model_type"]
    if model_type == WORD2VEC:
        wv = WordVectors(words=trained_model.wv.index_to_key, vectors=trained_model.wv.vectors)
        wv.to_file(save_path)
    else:
        print(f"ERROR: attempted to perform embedding with unknown model type: {model_type}")

def generate_sentencization(corpus: dict[str, any], SENTENCIZED_PREFIX):
    """
    corpus: dictionary representing a corpus, guaranteed to have keys corpus_name, corpus_path, corpus_id
    returns: None, it writes a sentencization to disk to be used for embedding generation later
    the sentencization written to disk has a name matching the corpus_id on the corpus passed in
    """
    plaintext_path = corpus["corpus_path"]
    sentencization_path = SENTENCIZED_PREFIX + corpus["corpus_id"] + ".txt"
    corpus["sentencized_path"] = sentencization_path
    with open(plaintext_path) as fin:
        text = "\n".join(fin.readlines())

    sentences = [word_tokenize(s) for s in sent_tokenize(text.lower())]
    with open(sentencization_path, "w+") as fout:
        for sent in sentences:
            fout.write("%s\n" % " ".join(sent))
def main(embeddings_config_path, APPLICATION_CONSTANTS_FILENAME):
    # read in constants
    with open(APPLICATION_CONSTANTS_FILENAME) as constants_file:
        app_constants = json.loads(constants_file.read())
    # Model type constants
    WORD2VEC = app_constants["MODEL_TYPES"]["WORD2VEC"]
    # contains all models that can be trained on the data
    TRAINABLE_MODELS = set(app_constants["TRAINABLE_MODEL_TYPES"].values())
    # File system constants imported from metadata file
    # folder where raw corpora are stored
    CORPORA_PREFIX = app_constants["CORPORA_PREFIX"]
    # folder where sentencized corpora are stored
    SENTENCIZED_PREFIX = app_constants["SENTENCIZED_PREFIX"]
    # folder where tokenizations are cached
    TOKENIZATION_PREFIX = app_constants["TOKENIZATION_PREFIX"]
    # folder where trained models are cached
    TRAINED_MODEL_PREFIX = app_constants["TRAINED_MODEL_PREFIX"]
    # folder where static models are stored (and later loaded from disk) 
    STATIC_MODEL_PREFIX = app_constants["STATIC_MODEL_PREFIX"]
    # folder where final embeddings are written 
    EMBEDDINGS_PREFIX = app_constants["EMBEDDINGS_PREFIX"]

    # crawl the config and generate embeddings that don't yet exist
    with open(embeddings_config_path) as config_file:
        config = json.loads(config_file.read())
    for corpus in config:
        if "corpus_id" not in corpus:
            # we have a brand new corpus
            corpus["corpus_id"] = str(uuid.uuid4())
            print(f"Found new corpus: {corpus['corpus_name']}.")
            print(f"Assigned new corpus id as: {corpus['corpus_id']}.")
            print(f"Generating sentencization for new corpus {corpus['corpus_name']}")
            generate_sentencization(corpus, SENTENCIZED_PREFIX)
        else:
            print(f"Found corpus with id: {corpus['corpus_name']}.")
        for tokenization in corpus["tokenizations"]:
            if "tokenization_id" not in tokenization:
                tokenization["tokenization_id"] = str(uuid.uuid4())
                print(f"Found new tokenization for {corpus['corpus_name']}:{tokenization['tokenization_name']}.")
                print(f"Assigned new tokenization id as: {tokenization['tokenization_id']}.")
                # do the tokenization and save it to disk
                tokenization_path = TOKENIZATION_PREFIX + tokenization["tokenization_id"] + ".pickle"
                tokenization["tokenization_path"] = tokenization_path 
                print(f"Performing tokenization for {corpus['corpus_name']}:{tokenization['tokenization_name']}.")
                # get the lines of the plaintext
                with open(corpus["sentencized_path"]) as plaintext:
                    sentences = plaintext.readlines()
                tokenized = preprocess(sentences, tokenization["tokenization_config"])
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
                if "model_id" not in model:
                    # we have a brand new model to make
                    model["model_id"] = str(uuid.uuid4())
                    print(f"Found new model for {corpus['corpus_name']}:{tokenization['tokenization_name']}:{model['model_name']}.")
                    print(f"Wrote new model id as: {model['model_id']}.")
                    if model["model_config"]["model_type"] in TRAINABLE_MODELS:
                        print(f"Model of type {model['model_config']['model_type']} training on corpus.")
                        model_path = TRAINED_MODEL_PREFIX + model["model_id"] + ".pickle"
                        model["model_path"] = model_path
                        model_to_use = set_model(tokenized, model["model_config"], WORD2VEC)
                        with open(model_path, "wb") as output_file:
                            pickle.dump(model_to_use, output_file)
                    else:
                        print(f"Model of type {model['model_config']['model_type']} is pretrained; loading from disk.")
                        # todo: load pretrained models from disk
                        with open(model["model_path"], "rb") as model_file:
                            model_to_use = pickle.load(model_file)
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
                        embedding["embedding_path"] = embedding_path
                        generated_embedding = embed(model_to_use, model["model_config"], tokenized, embedding["embedding_config"], embedding_path, WORD2VEC)
                    else:
                        # todo: integrity check - confirm the embedding file actually exists
                        print(f"Embedding already exists for {corpus['corpus_name']}:{tokenization['tokenization_name']}:{model['model_name']}:{embedding['embedding_name']}. No action taken.")
                        pass
    # if we successfully generated all the embeddings, overwrite the config file
    print("Successfully generated all embeddings specified by config, overwriting config with any new data")
    with open(embeddings_config_path, "w") as config_file:
        json.dump(config, config_file, indent=2)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("embeddings_config", type=str, help="path to embeddings configuration")
    args = parser.parse_args()
    # constants  
    APPLICATION_CONSTANTS_FILENAME = "app/metadata/application_constants.json"
    main(args.embeddings_config, APPLICATION_CONSTANTS_FILENAME)
