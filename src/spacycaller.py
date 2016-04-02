# spacycaller.py
# Gil Walzer

from spacy.en import English
class SpacyCaller():
    def __init__(self):
        self.nlp = English()
    
    def spacy_analyze_vendor(self, vendor):
        profile = vendor.profile
        tokens = self.nlp(profile)
        
        return tokens
        