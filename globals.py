"""
    Performs global initialization of variables to be used in app.py
"""

# WordVectors - store dicts mapping method -> data
# e.g: wv1['global'] and wv['s4'] get the wordvectors for global alignment and s4, respectively
wv1 = dict()
wv2 = dict()
sorted_words = dict()

# Mapping results
distances = dict()
indices = dict()