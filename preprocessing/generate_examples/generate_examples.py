import argparse
import argparse
import json
import uuid
from preprocessing.generate_examples.example import Example
# load app constants from file
with open("metadata/application_constants.json") as constants_file:
    app_constants = json.loads(constants_file.read())
# load all possible alignment configurations from file
ALIGNMENT_CONFIGS_FILENAME = app_constants["ALIGNMENT_CONFIGS"]
with open("metadata/alignment_configs.json") as alignment_configurations_file:
    alignment_configs = json.loads(alignment_configurations_file.read())

def generate_example(example):
    """
    example: dict() guaranteed to contain keys embedding_a_id, embedding_b_id, common_vocab_size, alignments 
    returns: None; it writes a pickled Example object to disk in the location specified by EXAMPLES_PREFIX in
    "metadata/application_constants.json"
    """

    e = Example()

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
            new_example_id = uuid.uuid4() 
            example["example_id"] = new_example_id
            generate_example(example)
    print("Successfully generated all examples specified by config, overwriting config with any new data")
    with open(args.examples_config, "w") as config_file:
        json.dump(examples_list, config_file, indent=2)


if __name__ == "__main__":
    main()