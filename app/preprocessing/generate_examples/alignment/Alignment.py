import numpy as np
from mapping import perform_mapping
from app.preprocessing.WordVectors import WordVectors
from global_align import GlobalAlignConfig 
from noise_aware_align import NoiseAwareAlignConfig 
from s4_align import S4AlignConfig 
class Alignment:
    """Implements an Alignment Object to be stored as part of an example"""
    def __init__(self, wv1, wv2, name, alignment_config):
        """
        generates an alignment object from wv1 and wv2
        wv1 and wv2 have already been intersected
        """
        # name of this alignment
        self.name = name
        # WordVectors object containing wv1 aligned to wv2
        wv1_aligned = self.align_using_config(wv1, wv2, alignment_config)
        # semantic shift for each word
        self.shifts = self.compute_shifts(wv1_aligned, wv2)
        # nearest neighbors for each word
        # nearest neighbors in b for each word in a
        self.a_b = perform_mapping(wv1.vectors, wv2.vectors)
        # nearest neighbors in a for each word in b
        self.b_a = perform_mapping(wv2.vectors, wv1.vectors)
        # not sure if I want to save Q and the anchors here
    def align_using_config(wv1, wv2, alignment_config):
        """
        aligns wv1 to wv2 using the provided alignment config
        """
        aligned, _, _ = alignment_config.align(wv1, wv2, alignment_config)
        return aligned
    def compute_shifts(wv1, wv2):
        """
        computes the semantic shift for each word in the example
        """
        d_cosine = np.array([np.cosine(u, v) for u, v in zip(wv1.vectors, wv2.vectors)])
        i_most_shifted = np.argsort(d_cosine)[::-1]  # Indices sorted by highest to lowers cosine distance
        out_words = [wv1.get_word(i) for i in i_most_shifted]
        out_scores = [float(d_cosine[i]) for i in i_most_shifted]
        return dict(zip(out_words, out_scores))

    
