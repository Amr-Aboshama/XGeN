# import random
#from nltk.stem import PorterStemmer

from QAGen.utilities import tokenize_sentences, get_sentences_for_keyword
from QAGen.QGen import QGen


class TFGen(QGen):

    def __init__(self, loader):
        QGen.__init__(self, loader)
            

    def predict_tf(self, keywords, modified_text, full_keywords):
        
        modified_text = modified_text.replace(".",". ")
        modified_text = modified_text.replace(".  ",". ")
        sentences = tokenize_sentences(modified_text)
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
            sentence = None
            for sent in keyword_sentence_mapping[key]:
                if self._QGen__regex_search(sent[:25], key) and sent not in used_sentences:
                    sentence = sent
                    used_sentences.append(sentence)
                    break

            if sentence is None:
                print('No sentence for key: ', key)
                continue

            answer = "T"
            # Make a false question
            if(bool(self.rand.getrandbits(1)) and self._QGen__regex_search(sentence, key)):
                option = self._QGen__find_alternative(key, full_keywords)
                correction = option + " -> " + key
                answer = "F,        " + correction

                sentence = self._QGen__replace_choice(sentence, key, option)
            #question = {"question": sentence, "answer": answer}
        #if(question not in output_array["questions"]):    
            output_array.append((sentence, answer))
                
        return output_array
