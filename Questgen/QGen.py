

class QGen:
    
    def __init__(self, loader):
        
        self.nlp = loader.nlp
        self.s2v = loader.s2v
        self.fdist = loader.fdist
        self.normalized_levenshtein = loader.normalized_levenshtein
 
        self.tokenizer = loader.tokenizer
        self.device = device
        self.model = model