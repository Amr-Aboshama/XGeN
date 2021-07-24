import torch
from QAGen.QGen import QGen
from QAGen.anspred.AnswerPredictor import AnswerPredictor


class ShortGen(QGen):

    def __init__(self, loader):
        QGen.__init__(self, loader)
        self.answerPredictor = AnswerPredictor(loader)


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
            
            generated_questions = self.__generate_normal_questions(keyword_sentence_mapping,self.device,self.tokenizer,self.qg_model)
            
            
        #final_output["statement"] = modified_text
        #final_output["questions"] = generated_questions["questions"]
        
        if torch.device=='cuda':
            torch.cuda.empty_cache()

        #return final_output
        return generated_questions


    def __generate_normal_questions(self,keyword_sent_mapping,device,tokenizer,model):  #for normal one word questions
        batch_text = []
        answers = keyword_sent_mapping.keys()
        for answer in answers:
            txt = keyword_sent_mapping[answer]
            context = "generate question: " + self._QGen__replace_choice(txt, answer, "<h1>" + answer + "<h1>") + " </s>"
            batch_text.append(context)
        
        encoding = tokenizer.batch_encode_plus(batch_text, pad_to_max_length=True, return_tensors="pt", max_length=512, truncation=True)
        input_ids, attention_masks = encoding["input_ids"].to(device), encoding["attention_mask"].to(device)

        with torch.no_grad():
            outs = model.generate(input_ids=input_ids,
                                attention_mask=attention_masks,
                                max_length=150)
            
        output_array = []
        #output_array["questions"] =[]
        wh_words = ['What', 'Where', 'When', 'How', 'Who', 'Why', 'How many', 'How much']
        
        selected_questions = set()

        for index, val in enumerate(answers):
            #individual_quest= {}
            out = outs[index, :]
            dec = tokenizer.decode(out, skip_special_tokens=True, clean_up_tokenization_spaces=True)
            
            Question= dec.replace('question:', '')
            Question= Question.strip()
            
            if any(Question.find(wh) == 0 for wh in wh_words):
                payload = {
                    "context": keyword_sent_mapping[val],
                    "question" : Question
                }
                print("predict answer")
                answer = self.__predict_answer(payload)
                print("Done prediction")
                if Question.find(answer[:-1].lower()) == -1 and Question not in selected_questions:
                    selected_questions.add(Question)
                    output_array.append((Question, answer))
                else:
                    print("the answer in the question, we ignored that question")
            
        return output_array


    def __predict_answer(self,payload):
        
        input = "question: %s <s> context: %s </s>" % (payload["question"], payload["context"])

        encoding = self.tokenizer.encode_plus(input, return_tensors="pt")
        input_ids, attention_masks = encoding["input_ids"].to(self.device), encoding["attention_mask"].to(self.device)
        greedy_output = self.model.generate(input_ids=input_ids, attention_mask=attention_masks, max_length=256)
        Question =  self.tokenizer.decode(greedy_output[0], skip_special_tokens=True,clean_up_tokenization_spaces=True)
        output = Question.strip().capitalize()

        return output

