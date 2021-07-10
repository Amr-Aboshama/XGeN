
class QGen:
    
    def __init__(self, loader):
        
        self.nlp = loader.nlp
        self.s2v = loader.s2v
        self.fdist = loader.fdist
        self.normalized_levenshtein = loader.normalized_levenshtein
 
        self.tokenizer = loader.tokenizer
        self.device = loader.device

        self.qg_model = loader.qg_model
        self.bq_model = loader.bq_model
        self.ap_model = loader.ap_model