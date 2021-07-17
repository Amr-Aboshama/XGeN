# import random
#from nltk.stem import PorterStemmer

from QAGen.utilities import tokenize_sentences, get_sentences_for_keyword
from QAGen.QGen import QGen


class TFGen(QGen):

    def __init__(self, loader):
        QGen.__init__(self, loader)
            

    def predict_tf(self, keywords, modified_text, full_keywords):

        sentences = tokenize_sentences(modified_text.replace(".",". "))
        keyword_sentence_mapping = get_sentences_for_keyword(keywords, sentences)
        
        if len(keyword_sentence_mapping.keys()) == 0:
            print('No keywords in this sentence')
            return []
            
        output_array = []
        #output_array["questions"] =[]

        used_sentences = []
        #key = self.rand.choice(list(keyword_sentence_mapping.keys()))
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
            if(bool(self.rand.getrandbits(1)) and sentence.find(key) != -1):
                option = self._QGen__find_alternative(key, full_keywords)
                correction = option + " -> " + key
                answer = "F,        " + correction

                sentence = self._QGen__replace_choice(sentence, key, option)
            #question = {"question": sentence, "answer": answer}
        #if(question not in output_array["questions"]):    
            output_array.append((sentence, answer))
                
        return output_array
