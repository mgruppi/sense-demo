from app.preprocessing.WordVectors import WordVectors
from app.preprocessing.generate_examples.alignment.Alignment import Alignment
import numpy as np
class Example:
    """
    this class contains the precomputed data and utility functions for
    a single combination that can be selected in the user interface
    """
    def __init__(self, id,  embedding1, embedding2, alignment_configs, pt1_path, pt2_path):
        """
        Initializes an Example object
        id: str id of the example object (this will be saved to disk)
        embedding1: WordVectors object representing the first embedding
        embedding2: WordVectors object representing the second embedding
        alignments: a list of alignment configs to use to generate alignments for this combination
        pt1_path: path to the sentencized plaintext file that was used to generate embedding1
        pt2_path: path to the sentencized plaintext file that was used to generate embedding2
        """
        # id for this example object
        self.id = id
        # list of words the two embeddings have in common
        self.common_words= self.intersection_words(embedding1, embedding2)
        # list of alignment objects 
        self.alignments = self.generate_alignments(embedding1, embedding2, alignment_configs)
        self.embedding1_sample_sentences = self.sample_sentences(pt1_path)
        self.embedding2_sample_sentences = self.sample_sentences(pt2_path)
    def generate_alignments(self, wv1, wv2, alignment_configs):
        """generates a list of alignment objects from a list of alignment configs and two wordvectors objects"""
        # intersect the two wordvectors so they only contain overlapping words
        # this is done here so we don't have to re-intersect per-alignment
        _wv1, _wv2 = WordVectors.intersect(wv1, wv2)
        alignments = []
        for alignment_config in alignment_configs:
            alignments.append(Alignment(_wv1, _wv2, alignment_config))
        return alignments
    def sample_sentences(self, path, nsamples = 200000):
        """
        return a list of nsamples lines from the text file at path
        """
        with open(path) as file_handle:
            sents = [s.rstrip() for s in file_handle.readlines()]
        if len(sents) > nsamples:
            sample_indices = np.random.choice(len(sents), size=nsamples)
        return [sents[i] for i in sample_indices]
    def intersection_words(self, wv1: WordVectors, wv2: WordVectors):
        """
        returns a list of words in common between wv1 and wv2
        """
        common = set.intersection(set(wv1.get_words()), set(wv2.get_words()))
        return list(common)
