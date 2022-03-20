import unittest
from app.preprocessing.WordVectors import WordVectors
class WordVectorsTest(unittest.TestCase):
    def test_wordvectors_initialization_from_disk(self):
        input_path = "test/test_data/wordvectors_short.txt"
        wv = WordVectors(input_file = input_path)
        print(wv.dimension)
        print(wv.words)
        print(wv.word_id)
        print(wv.vectors)
        assert(True)
if __name__ == '__main__':
    unittest.main()