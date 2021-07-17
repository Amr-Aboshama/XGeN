import re
import time
# import random
from QAGen.utilities import tokenize_sentences, get_sentences_for_keyword

from QAGen.QGen import QGen


class MCQGen(QGen):

    def __init__(self, loader):
        QGen.__init__(self, loader)

        
    def predict_mcq(self, keywords, modified_text, full_keywords):
        sentences = tokenize_sentences(modified_text)
        
        keyword_sentence_mapping = get_sentences_for_keyword(keywords, sentences)
        for k in keyword_sentence_mapping.keys():
            text_snippet = " ".join(keyword_sentence_mapping[k][:1])
            keyword_sentence_mapping[k] = text_snippet
        
        #final_output = {}

        if len(keyword_sentence_mapping.keys()) == 0:
            return []
        else:
            try:
                generated_questions = self.__generate_questions_mcq(keyword_sentence_mapping, full_keywords)

            except:
                #return final_output
                return []

            
            #return final_output
            return generated_questions


    def __replace_choice(self, sentence, val):
        
        # The next line to replace with case insensitive
        esc_val = re.escape(val)
        sentence = re.sub(rf'(\s){esc_val}(\s)', r' ____ ', sentence, flags=re.IGNORECASE)
        sentence = re.sub(rf'(\s){esc_val}([.,!?])', r' ____\2', sentence, flags=re.IGNORECASE)
        sentence = re.sub(rf'(^)Hello(\s)', r'____ ', sentence, flags=re.IGNORECASE)
        sentence = re.sub(rf'(\s)Hello($)', r' ____', sentence, flags=re.IGNORECASE)

        return sentence

    def __generate_questions_mcq(self, keyword_sentence_mapping, full_keywords):
        answers = keyword_sentence_mapping.keys()
        output_array = []
        #output_array["questions"] = []
        used_sentences = []

        for index, val in enumerate(answers):
            sentence = keyword_sentence_mapping[val]
            if sentence in used_sentences:
                continue
            
            #individual_question ={}
            
            context = self.__replace_choice(sentence, val)
            
            options, answer = self._QGen__get_options(val, full_keywords)
            # options =  filter_phrases(options, 10, self.normalized_levenshtein)


            #output_array["questions"].append(individual_question)
            output_array.append((context,answer, options))

            used_sentences.append(sentence)
            

        return output_array