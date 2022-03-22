import shutil
import unittest
from ....app.preprocessing.WordVectors import WordVectors
from ....app.preprocessing.generate_embeddings.generate_embeddings import main as generate_embeddings_main
class GenerateEmbeddingsTest(unittest.TestCase):
    def setUp(self):
        # create a working copy of the test json file
        self.test_file_back_path = "test/preprocessing/generate_embeddings/test_data/embeddings_config_test_back.json"
        self.test_file_path = "test/preprocessing/generate_embeddings/test_data/embeddings_config_test.json"
        self.app_constants_test_path = "test/preprocessing/generate_embeddings/test_data/test_application_constants.json"
        shutil.copyfile(self.test_file_back_path, self.test_file_path)
    def tearDown(self):
        # remove embeddings generated during test
        # remove models generated during test
        # remove sentencizations generated during test
        # remove tokenizations generated during test
        assert(True)
    def test_embedding_generation(self):
        generate_embeddings_main(self.test_file_path, self.app_constants_test_path)
        # check the tokenizations are on disk as expected
        # check the sentencizations are on disk as expected
        # check the models are on disk as expected
        # check the embeddings are on disk as expected
        # todo test wordvectors
        assert(True)
if __name__ == '__main__':
    unittest.main()