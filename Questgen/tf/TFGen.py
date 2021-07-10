import re
import random
from Questgen.utilities import tokenize_sentences, get_keywords, get_sentences_for_keyword, \
                            get_options
from Questgen.QGen import QGen


class TFGen(QGen):

    def __init__(self, loader):
        QGen.__init__(self, loader)
            

    def predict_tf(self,payload):
        
        text = payload.get("input_text")
        topics_num = payload.get('topics_num')
        sentences = tokenize_sentences(text)
        joiner = " "
        modified_text = joiner.join(sentences)
        
        keywords = get_keywords(self.nlp,modified_text,topics_num,self.s2v,self.fdist,self.normalized_levenshtein,len(sentences) )

        keyword_sentence_mapping = get_sentences_for_keyword(keywords, sentences)
        
        output_array ={}
        output_array["questions"] =[]

        for key in keyword_sentence_mapping.keys():
            sentence = keyword_sentence_mapping[key][0]
            
            answer = "T"
            # Make a false question
            if(bool(random.getrandbits(1))):
                options = get_options(key, self.s2v)
                correction = options[0][0] + " -> " + key
                answer = "F,        " + correction
                sentence = re.sub(re.escape(key), options[0][0], sentence, flags=re.IGNORECASE)
            
            output_array["questions"].append({"question": sentence, "answer": answer})
                    
        return output_array
    