import shutil
import unittest

from numpy import delete
from app.preprocessing.WordVectors import WordVectors
from app.preprocessing.generate_embeddings.generate_embeddings import main as generate_embeddings_main
import os
import json
def delete_files_in_dir(path):
    files = os.listdir(path)
    for file in files:
        # todo handle file paths properly
        if path[-1] == '/':
            os.remove(path + file)
        else:
            os.remove(path + "/" + file)
class GenerateEmbeddingsTest(unittest.TestCase):
    def setUp(self):
        # create a working copy of the test json file
        self.embeddings_file_back_path = "test/preprocessing/generate_embeddings/test_data/metadata/embeddings_config_test_back.json"
        self.embeddings_file_path ="test/preprocessing/generate_embeddings/test_data/metadata/embeddings_config_test.json"
        self.app_constants_test_path = "test/preprocessing/generate_embeddings/test_data/metadata/test_application_constants.json"
        shutil.copyfile(self.embeddings_file_back_path, self.embeddings_file_path)
    def tearDown(self):
        with open(self.app_constants_test_path) as app_constants_file_handle:
            app_constants = json.loads(app_constants_file_handle.read())
        # remove embeddings generated during test
        delete_files_in_dir(app_constants["EMBEDDINGS_PREFIX"])
        # remove models generated during test
        delete_files_in_dir(app_constants["TRAINED_MODEL_PREFIX"])
        delete_files_in_dir(app_constants["STATIC_MODEL_PREFIX"])
        # remove sentencizations generated during test
        delete_files_in_dir(app_constants["SENTENCIZED_PREFIX"])
        # remove tokenizations generated during test
        delete_files_in_dir(app_constants["TOKENIZATION_PREFIX"])
        assert(True)
    def test_embedding_generation(self):
        generate_embeddings_main(self.embeddings_file_path, self.app_constants_test_path)
        # todo make actual assertions, not crashing is good enough for now
        # check the tokenizations are on disk as expected
        # check the sentencizations are on disk as expected
        # check the models are on disk as expected
        # check the embeddings are on disk as expected
        # todo test wordvectors
        assert(True)
if __name__ == '__main__':
    unittest.main()