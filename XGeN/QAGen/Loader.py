import torch
from transformers import T5ForConditionalGeneration,T5Tokenizer
import random
from datetime import datetime
from similarity.normalized_levenshtein import NormalizedLevenshtein


class Loader:
    '''
        Load the common models and tools of the project.
    '''
    
    def __init__(self
    , qg_model_path = 'valhalla/t5-base-qa-qg-hl'
    , bq_model_path = '/content/gdrive/MyDrive/models/boolq'
    , t5_tokenizer_path = 't5-base'):
        
        self.tokenizer = T5Tokenizer.from_pretrained(t5_tokenizer_path)
        self.tokenizer.add_tokens(['<sep>', '<hl>'])
        self.normalized_levenshtein = NormalizedLevenshtein()
        self.rand = random.Random(datetime.now())
        
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.qg_model = T5ForConditionalGeneration.from_pretrained(qg_model_path).to(self.device)
        self.bq_model = T5ForConditionalGeneration.from_pretrained(bq_model_path).to(self.device)
        