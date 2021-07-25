from QAGen.QGen import QGen


class TFGen(QGen):

    def __init__(self, loader):
        QGen.__init__(self, loader)
            

    def generate(self, keyword_sentence_mapping, full_keywords):
        '''
            Input: dictionary (keyword -> sentences), list of string (full keywords)
            Output: list of questions
            -------------------------------------------------------------------------
            Generate list of T/F Questions with answers and corrections.
        '''
        
        if len(keyword_sentence_mapping.keys()) == 0:
            print('No keywords in this sentence')
            return []
            
        output_array = []

        used_sentences = []
        for key in keyword_sentence_mapping.keys():
            # choosing a sentence not used before
            sentence = None
            for sent in keyword_sentence_mapping[key]:
                if self._QGen__regex_search(sent, key) == 1 \
                    and sent not in used_sentences:

                    sentence = sent
                    used_sentences.append(sentence)
                    break

            if sentence is None:
                print('No sentence for key: ', key)
                continue

            answer = "T"
            # Make a false question
            if(bool(self.rand.getrandbits(1)) and self._QGen__regex_search(sentence, key)):
                option = self._QGen__find_alternative(sentence, key, full_keywords)
                correction = option + " -> " + key
                answer = "F,        " + correction

                sentence = self._QGen__replace_choice(sentence, key, option)

            sentence = sentence.capitalize()            
            output_array.append((sentence, answer))
                
        return output_array
