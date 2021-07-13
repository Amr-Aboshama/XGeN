import re
import random
from difflib import SequenceMatcher
#from nltk.stem import PorterStemmer

from QAGen.utilities import tokenize_sentences, get_sentences_for_keyword, get_options
from QAGen.QGen import QGen


class TFGen(QGen):

    def __init__(self, loader):
        QGen.__init__(self, loader)
            

    def predict_tf(self, keywords, modified_text):

        sentences = tokenize_sentences(modified_text.replace(".",". "))
        keyword_sentence_mapping = get_sentences_for_keyword(keywords, sentences)
        
        output_array = []
        #output_array["questions"] =[]

        used_sentences = []
        #key = random.choice(list(keyword_sentence_mapping.keys()))
        for key in keyword_sentence_mapping.keys():
            # choosing a sentence not used before
            sentence = keyword_sentence_mapping[key][0]
            found_sentence = False
            for sentence in keyword_sentence_mapping[key]:
                if sentence not in used_sentences:
                    used_sentences.append(sentence)
                    found_sentence = True
                    break
            
            if not found_sentence:
                continue
            
            answer = "T"
            # Make a false question
            if(bool(random.getrandbits(1)) and sentence.find(key) != -1):
                option = self.find_alternative(key)
                if option != key:
                    correction = option + " -> " + key
                    answer = "F,        " + correction
                    sentence = re.sub(re.escape(key), option, sentence, flags=re.IGNORECASE)
            #question = {"question": sentence, "answer": answer}
        #if(question not in output_array["questions"]):    
            output_array.append((sentence, answer))
                
        return output_array

    
    def find_alternative(self, key):
        options = get_options(key, self.s2v)
        
        #if len(options[0]):
        #    option = options[0][0]
            # Note: The next line may cause an infinite loop
            #while SequenceMatcher(None, option.lower(), key.lower()).ratio() > 0.7:
            #    print(option, key, SequenceMatcher(None, option, key).ratio())
            #    option = random.choice(options[0])
        for option in options[0]:
            if SequenceMatcher(None, option.lower(), key.lower()).ratio() < 0.7:
                #print(option, key, SequenceMatcher(None, option, key).ratio())
                return option
        return key