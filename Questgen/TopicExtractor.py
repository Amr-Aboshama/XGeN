from Questgen.utilities import tokenize_sentences, get_keywords, get_sentences_for_keyword
import spacy
from sense2vec import Sense2Vec
from nltk import FreqDist
from nltk.corpus import brown
from similarity.normalized_levenshtein import NormalizedLevenshtein


class TopicExtractor:

    def __init__(self):
        
        self.nlp = spacy.load('en_core_web_sm')
        self.s2v = Sense2Vec().from_disk('s2v_old')
        self.fdist = FreqDist(brown.words())
        self.normalized_levenshtein = NormalizedLevenshtein()


    def extract_keywords(self, payload):
        text = payload.get("input_text")
        topics_num = payload.get('topics_num')
        sentences = tokenize_sentences(text)
        joiner = " "
        modified_text = joiner.join(sentences)
        
        keywords = get_keywords(self.nlp,modified_text,topics_num,self.s2v,self.fdist,self.normalized_levenshtein,len(sentences) )

        keyword_sentence_mapping = get_sentences_for_keyword(keywords, sentences)

        for k in keyword_sentence_mapping.keys():
            text_snippet = " ".join(keyword_sentence_mapping[k][:3])
            keyword_sentence_mapping[k] = text_snippet

        return keyword_sentence_mapping, modified_text
