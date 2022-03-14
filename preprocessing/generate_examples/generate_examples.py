import argparse
import argparse
import json
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("path_to_config", type=str, help="Path to configuration file for example generation")
    args = parser.parse_args()
    with open("metadata/examples_config.json") as examples_config_file:
        examples_list = json.loads(examples_config_file.read())
    # crawl each example and generate it if necessary
    for example in examples_list:
        if "example_id" not in example:
            # we should generate this example again

if __name__ == "__main__":
    main()