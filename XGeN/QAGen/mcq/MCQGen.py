from QAGen.QGen import QGen


class MCQGen(QGen):

    def __init__(self, loader):
        QGen.__init__(self, loader)


    def generate(self, keyword_sentence_mapping, full_keywords):
        '''
            Input: dictionary (keyword -> sentences), list of string (full keywords)
            Output: list of questions
            -------------------------------------------------------------------------
            Generate list of MCQ with answers.
        '''
        
        if len(keyword_sentence_mapping.keys()) == 0:
            print('No keywords in this sentence')
            return []
        else:
            try:
                generated_questions = self.__generate_questions_mcq(keyword_sentence_mapping, full_keywords)

            except:
                #return final_output
                return []

            
            #return final_output
            return generated_questions


    def __generate_questions_mcq(self, keyword_sentence_mapping, full_keywords):
        answers = keyword_sentence_mapping.keys()
        output_array = []
        used_sentences = []

        for index, key in enumerate(answers):
            # choosing a sentence not used before
            sentence = None
            for sent in keyword_sentence_mapping[key]:
                if sent not in used_sentences:
                    
                    sentence = sent
                    used_sentences.append(sentence)
                    break

            if sentence is None:
                print('No sentence for key: ', key)
                continue
            
            # Remove the answer from the question. 
            context = self._QGen__replace_choice(sentence, key)
            context = context.capitalize()

            # Generate list of options.
            options, answer = self._QGen__get_options(key, full_keywords, none_exist=True)

            # Capitalize the first character
            if context[0] == '_':
                answer = answer.capitalize()
                options = [o.capitalize() for o in options]


            output_array.append((context,answer, options))

            used_sentences.append(sentence)
            

        return output_array