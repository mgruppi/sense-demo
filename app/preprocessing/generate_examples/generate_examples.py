import argparse
import argparse
import json
import uuid
from xmlrpc.client import APPLICATION_ERROR
from ..WordVectors import WordVectors
from .example import Example
from .alignment.global_align import GlobalAlignConfig
from .alignment.s4_align import S4AlignConfig 
from .alignment.noise_aware_align import NoiseAwareAlignConfig
import pickle
# load app constants from file
APPLICATION_CONSTANTS_FILENAME = "app/metadata/application_constants.json" 
with open(APPLICATION_CONSTANTS_FILENAME) as constants_file:
    app_constants = json.loads(constants_file.read())
# load all possible alignment configurations from file
ALIGNMENT_CONFIGS_FILENAME = app_constants["ALIGNMENT_CONFIGS"]
EMBEDDING_PREFIX = app_constants["EMBEDDINGS_PREFIX"]
EXAMPLE_PREFIX = app_constants["EXAMPLES_PREFIX"]
with open(ALIGNMENT_CONFIGS_FILENAME) as alignment_configurations_file:
    all_alignment_configs = json.loads(alignment_configurations_file.read())

def generate_example(new_example_id, example):
    """
    new_example_id: str uuid4 to be saved alongside the example object
    example: dict() guaranteed to contain keys embedding_a_id, embedding_b_id, common_vocab_size, alignments 
    returns: None; it writes a pickled Example object to disk in the location specified by EXAMPLES_PREFIX in
    "metadata/application_constants.json"
    """
    # create an alignment config object for each alignment in the input
    # todo factor constants out of code here
    config_objs = []
    for cfg in example["alignments"]:
        print(cfg)
        a_type = all_alignment_configs[cfg["name"]]["alignment_type"]
        args = all_alignment_configs[cfg["name"]]["args"]
        if a_type == "s4":
            config_objs.append(S4AlignConfig(*args))
        elif a_type == "global":
            config_objs.append(GlobalAlignConfig(*args))
        elif a_type == "noise_aware":
            config_objs.append(NoiseAwareAlignConfig(*args))
        else:
            raise ValueError("Unknown alignment type encountered in config")
    # load embedding one and two from disk
    # todo system agnostic filepath handling
    wv1_path = EMBEDDING_PREFIX + example["embedding_a_id"] + ".pickle"
    wv2_path = EMBEDDING_PREFIX + example["embedding_b_id"] + ".pickle"
    wv1 = WordVectors.from_file(wv1_path)
    wv2 = WordVectors.from_file(wv2_path)
    return Example(new_example_id, wv1, wv2, config_objs)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("examples_config", type=str, help="Path to configuration file for example generation")
    args = parser.parse_args()
    with open(args.examples_config) as examples_config_file:
        examples_list = json.loads(examples_config_file.read())
    # crawl each example and generate it if necessary
    for example in examples_list:
        if "example_id" not in example:
            # we should generate this example since it hasn't yet been generated
            new_example_id = str(uuid.uuid4())
            example["example_id"] = new_example_id
            e = generate_example(new_example_id, example)
            # todo proper file name handling 
            with open(EXAMPLE_PREFIX+new_example_id+".pickle", "wb") as fout:
                pickle.dump(e, fout)
    print("Successfully generated all examples specified by config, overwriting config with any new data")
    with open(args.examples_config, "w") as config_file:
        json.dump(examples_list, config_file, indent=2)


if __name__ == "__main__":
    main()