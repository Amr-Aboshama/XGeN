import torch
from QAGen.QGen import QGen


class ShortGen(QGen):

    def __init__(self, loader, ansPredict):
        QGen.__init__(self, loader)
        self.ansPredict = ansPredict
        

    def generate(self, keyword_sentence_mapping, _):
        
        for k in keyword_sentence_mapping.keys():
            ks_len = len(keyword_sentence_mapping[k])
            text_snippet = " ".join(keyword_sentence_mapping[k][:min(3, ks_len)])
            keyword_sentence_mapping[k] = text_snippet

        #final_output = {}

        if len(keyword_sentence_mapping.keys()) == 0:
            print('No keywords in this sentence')
            return []
        else:
            
            generated_questions = self.__generate_normal_questions(keyword_sentence_mapping)
            
            
        #final_output["statement"] = modified_text
        #final_output["questions"] = generated_questions["questions"]
        
        if torch.device=='cuda':
            torch.cuda.empty_cache()

        #return final_output
        return generated_questions


    def __generate_normal_questions(self,keyword_sent_mapping):  #for normal one word questions
        batch_text = []
        answers = keyword_sent_mapping.keys()
        for answer in answers:
            txt = keyword_sent_mapping[answer]
            context = "generate question: " + self._QGen__replace_choice(txt, answer, "<hl>" + answer + "<hl>") + " </s>"
            batch_text.append(context)
        
        encoding = self.tokenizer.batch_encode_plus(batch_text, pad_to_max_length=True, return_tensors="pt", max_length=512, truncation=True)
        input_ids, attention_masks = encoding["input_ids"].to(self.device), encoding["attention_mask"].to(self.device)

        with torch.no_grad():
            outs = self.model.generate(input_ids=input_ids,
                                attention_mask=attention_masks,
                                max_length=150)
            
        output_array = []
        #output_array["questions"] =[]
        #wh_words = ['What', 'Where', 'When', 'How', 'Who', 'Why', 'How many', 'How much']
        
        selected_questions = set()

        for index, val in enumerate(answers):
            #individual_quest= {}
            out = outs[index, :]
            dec = self.tokenizer.decode(out, skip_special_tokens=True, clean_up_tokenization_spaces=True)
            
            Question= dec.replace('question:', '')
            Question= Question.strip()
            
            payload = {
                "context": keyword_sent_mapping[val],
                "question" : Question
            }
            print("predict answer")
            answer = self.ansPredict.predict_answer(payload)
            print("Done prediction")
            if Question.find(answer[:-1].lower()) == -1 and Question not in selected_questions:
                selected_questions.add(Question)
                output_array.append((Question, answer))
            else:
                print("the answer in the question, we ignored that question")
                
        return output_array



