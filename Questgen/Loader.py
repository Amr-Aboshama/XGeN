import torch
from transformers import T5ForConditionalGeneration,T5Tokenizer
import spacy
import os
from sense2vec import Sense2Vec
from nltk import FreqDist
from nltk.corpus import brown
from similarity.normalized_levenshtein import NormalizedLevenshtein


class Loader:
    def __init__(self):
        
        self.tokenizer = T5Tokenizer.from_pretrained('t5-base')
        
        self.nlp = spacy.load('en_core_web_sm')
 
        self.s2v = Sense2Vec().from_disk('s2v_old')
        
        model = T5ForConditionalGeneration.from_pretrained(os.getcwd()+"/Questgen/models/question_generator")
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        model.to(device)
        self.device = device
        self.model = model
        
        self.fdist = FreqDist(brown.words())
        self.normalized_levenshtein = NormalizedLevenshtein()
    