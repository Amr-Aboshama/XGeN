import re
import time
import random
from QAGen.utilities import tokenize_sentences, get_keywords, get_sentences_for_keyword, \
                             filter_phrases, get_options

from QAGen.QGen import QGen


class MCQGen(QGen):

    def __init__(self, loader):
        QGen.__init__(self, loader)

        
    def predict_mcq(self, keywords, modified_text):
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
                generated_questions = self.__generate_questions_mcq(keyword_sentence_mapping,self.s2v)

            except:
                #return final_output
                return []

            #final_output["statement"] = modified_text
            #final_output["questions"] = generated_questions["questions"]
            
            #return final_output
            return generated_questions

    def __generate_questions_mcq(self, keyword_sentence_mapping,sense2vec):
        answers = keyword_sentence_mapping.keys()
        output_array = []
        #output_array["questions"] = []
        used_sentences = []

        for index, val in enumerate(answers):
            sentence = keyword_sentence_mapping[val]
            if sentence in used_sentences:
                continue
            
            #individual_question ={}
            
            # The next line to replace with case insensitive
            context = re.sub(re.escape(val), "____", sentence, flags=re.IGNORECASE)
            options, _ = get_options(val, sense2vec)
            options =  filter_phrases(options, 10, self.normalized_levenshtein)

            random_options = []
            while(len(options) > 0 and len(random_options) < 3):
                option = random.choice(options)
                random_options.append(option)
                options.remove(option)
            
            #individual_question["context"] = context
            #individual_question["question_type"] = "MCQ"
            #individual_question["answer"] = val
            #individual_question["id"] = index+1
            #individual_question["options"], individual_question["options_algorithm"] = get_options(val, sense2vec)
            #individual_question["options"] =  filter_phrases(individual_question["options"], 10,normalized_levenshtein)
            #index = 3
            #individual_question["extra_options"]= individual_question["options"][index:]
            #individual_question["options"] = individual_question["options"][:index]
            
            if len(random_options)>0:
                random_options.insert(random.randint(0,len(options)),val)
                if(len(random_options) < 4):
                    random_options.append("All of the above")
                if(len(random_options) < 4):
                    random_options.append("None of the above")

                #output_array["questions"].append(individual_question)
                output_array.append((context,val, random_options))

                used_sentences.append(sentence)
            

        return output_array