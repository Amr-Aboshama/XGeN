import re
import time
from Questgen.utilities import tokenize_sentences, get_keywords, get_sentences_for_keyword, \
                             filter_phrases, get_options

from Questgen.QGen import QGen


class MCQGen(QGen):

    def __init__(self, loader):
        QGen.__init__(self, loader)

        
    def predict_mcq(self, keyword_sentence_mapping, modified_text):
        
        final_output = {}

        if len(keyword_sentence_mapping.keys()) == 0:
            return final_output
        else:
            try:
                generated_questions = self.__generate_questions_mcq(keyword_sentence_mapping,self.s2v,self.normalized_levenshtein)

            except:
                return final_output

            final_output["statement"] = modified_text
            final_output["questions"] = generated_questions["questions"]
            
            return final_output


    def __generate_questions_mcq(self, keyword_sent_mapping,sense2vec,normalized_levenshtein):
        answers = keyword_sent_mapping.keys()
        output_array = {}
        output_array["questions"] = []

        for index, val in enumerate(answers):
            individual_question ={}
            # The next line to replace with case insensitive
            context = re.sub(re.escape(val), "____", keyword_sent_mapping[val], flags=re.IGNORECASE)
            individual_question["context"] = context
            individual_question["question_type"] = "MCQ"
            individual_question["answer"] = val
            individual_question["id"] = index+1
            individual_question["options"], individual_question["options_algorithm"] = get_options(val, sense2vec)
            individual_question["options"] =  filter_phrases(individual_question["options"], 10,normalized_levenshtein)
            index = 3
            individual_question["extra_options"]= individual_question["options"][index:]
            individual_question["options"] = individual_question["options"][:index]
            
            if len(individual_question["options"])>0:
                output_array["questions"].append(individual_question)

        return output_array