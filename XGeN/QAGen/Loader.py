import torch
from transformers import T5ForConditionalGeneration,T5Tokenizer
import spacy
import os
from sense2vec import Sense2Vec
from nltk import FreqDist
from nltk.corpus import brown
from similarity.normalized_levenshtein import NormalizedLevenshtein


class Loader:
    def __init__(self
    , s2v_model_path = os.getcwd()+"/QAGen/models/s2v_old"
    , qg_model_path = os.getcwd()+"/QAGen/models/question_generator"
    , bq_model_path = os.getcwd()+"/QAGen/models/t5_boolean_questions"
    , ap_model_path = os.getcwd()+"/QAGen/models/answer_predictor"
    , t5_tokenizer_path = 't5-base'):
        
        self.tokenizer = T5Tokenizer.from_pretrained(t5_tokenizer_path)
        # self.nlp = spacy.load('en_core_web_sm')
        self.s2v = Sense2Vec().from_disk(s2v_model_path)
        # self.fdist = FreqDist()
        self.normalized_levenshtein = NormalizedLevenshtein()
        
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.qg_model = T5ForConditionalGeneration.from_pretrained(qg_model_path).to(self.device)
        #self.bq_model = T5ForConditionalGeneration.from_pretrained(bq_model_path).to(self.device)
        #self.ap_model = T5ForConditionalGeneration.from_pretrained(ap_model_path).to(self.device) 
        
        #self.tokenizer = None
        self.nlp = None
        #self.s2v = None
        self.fdist = None
        #self.normalized_levenshtein = None
        
        #self.device = None
        #self.qg_model = None
        self.bq_model = None
        self.ap_model = None   