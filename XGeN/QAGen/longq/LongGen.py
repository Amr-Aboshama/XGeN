import torch
from QAGen.QGen import QGen
from QAGen.anspred.AnswerPredictor import AnswerPredictor


class LongGen(QGen):
    
    def __init__(self, loader):
        QGen.__init__(self, loader)
        self.answerPredictor = AnswerPredictor(loader)

  
    def paraphrase(self,text, q_num = 3):
        
        self.sentence= text
        self.text= "paraphrase: " + self.sentence + " </s>"

        encoding = self.tokenizer.encode_plus(self.text,pad_to_max_length=True, return_tensors="pt", max_length=512, truncation=True)
        input_ids, attention_masks = encoding["input_ids"].to(self.device), encoding["attention_mask"].to(self.device)

        beam_outputs = self.qg_model.generate(
            input_ids=input_ids,
            attention_mask=attention_masks,
            max_length= 50,
            num_beams=50,
            num_return_sequences=q_num,
            no_repeat_ngram_size=2,
            early_stopping=True
            )

        final_outputs =[]
        for beam_output in beam_outputs:
            sent = self.tokenizer.decode(beam_output, skip_special_tokens=True,clean_up_tokenization_spaces=True)
            if sent.lower() != self.sentence.lower() and sent not in final_outputs:
                question = sent.replace('ParaphrasedTarget: ', '')
                payload = {
                    "input_text": text,
                    "input_question" : question
                }
                answer = self.answerPredictor.predict_answer(payload)
                #final_outputs.append(sent.replace('ParaphrasedTarget: ', ''))
                final_outputs.append((question, answer))

        #output= {}
        #output['Paragraph']= text
        #output['Count']= q_num
        #output['Paraphrased Questions']= final_outputs
        

        if torch.device=='cuda':
            torch.cuda.empty_cache()
        
        #return output
        return final_outputs
