from app.preprocessing.WordVectors import WordVectors
class Alignment:
    """Implements an alignment type to be stored as part of an example"""
    def __init__(self, wv1, wv2, name, alignment_config):
        self.name = name
        self.alignment_type= alignment_config["alignment_type"]
        self.shifts = self.align(self.alignment_type, wv1, wv2)
    def s4_align(wv1, wv2, config):
    def global_align(wv1, wv2, config):
    def noise_aware_align(wv1, wv2, config):
    def align(a_type, wv1, wv2):
        if a_type == "s4":
    
