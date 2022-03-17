class Example:
    """
    this class contains the precomputed data and utility functions for
    a single combination that can be selected in the user interface
    """
    def __init__(self, id,  embedding1, embedding2, alignments):
        self.id = id
        """words in common between embedding1 and embedding2"""
        self.intersection_words = self.intersection_words(embedding1, embedding2)
        """
        dictionary where 
        keys are alignment configuration names
        values are dictionaries where
        keys are "shifts", "ab", "ba"
        "shifts" contains a dictionary where keys are words, values are numbers representing shifts
        "ab" contains a dict where the keys are words in a and the values are lists where each list contains indices corresponding to locations in 
        self.intersection_words sorted by which are closest to the current key
        "ba" contains a dict where the keys are words in b and the values are lists where each list contains indices corresponding to locations in 
        self.intersection_words sorted by which are closest to the current key
        """
        self.alignments = self.generate_alignments(alignments)
    def generate_alignment(self, alignments):
        # todo write this
        return dict()
    def intersection_words(self, embedding1, embedding2):
        # todo write this
        return []
