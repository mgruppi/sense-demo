from app.preprocessing.WordVectors import WordVectors
from app.preprocessing.generate_examples.alignment.Alignment import Alignment

class Example:
    """
    this class contains the precomputed data and utility functions for
    a single combination that can be selected in the user interface
    """
    def __init__(self, id,  embedding1, embedding2, alignment_configs):
        """
        Initializes an Example object
        id: str id of the example object (this will be saved to disk)
        embedding1: WordVectors object representing the first embedding
        embedding2: WordVectors object representing the second embedding
        alignments: a list of alignment configs to use to generate alignments for this combination
        """
        # id for this example object
        self.id = id
        # list of words the two embeddings have in common
        self.common_words= self.intersection_words(embedding1, embedding2)
        self.alignments = self.generate_alignments(embedding1, embedding2, alignment_configs)
    def generate_alignments(wv1, wv2, alignment_configs):
        alignments = []
        for alignment_config in alignment_configs:
            alignments.append(Alignment(wv1, wv2, alignment_config))
        return alignments
    def intersection_words(wv1: WordVectors, wv2: WordVectors):
        common = set.intersection(set(wv1.get_words()), set(wv2.get_words()))
        return list(common)
