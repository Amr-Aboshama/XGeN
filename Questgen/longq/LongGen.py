import torch
import os
from Questgen.utilities import tokenize_sentences, get_keywords, get_sentences_for_keyword
from QGen import QGen


class LongGen(QGen):
    
    def __init__(self, loader):
        QGen.__init__(self, loader)

  
    def paraphrase(self,payload):
        
        text = payload.get("input_text")
        num = payload.get("max_questions", 3)
        
        self.sentence= text
        self.text= "paraphrase: " + self.sentence + " </s>"

        encoding = self.tokenizer.encode_plus(self.text,pad_to_max_length=True, return_tensors="pt")
        input_ids, attention_masks = encoding["input_ids"].to(self.device), encoding["attention_mask"].to(self.device)

        beam_outputs = self.model.generate(
            input_ids=input_ids,
            attention_mask=attention_masks,
            max_length= 50,
            num_beams=50,
            num_return_sequences=num,
            no_repeat_ngram_size=2,
            early_stopping=True
            )

        final_outputs =[]
        for beam_output in beam_outputs:
            sent = self.tokenizer.decode(beam_output, skip_special_tokens=True,clean_up_tokenization_spaces=True)
            if sent.lower() != self.sentence.lower() and sent not in final_outputs:
                final_outputs.append(sent.replace('ParaphrasedTarget: ', ''))
        
        output= {}
        output['Paragraph']= text
        output['Count']= num
        output['Paraphrased Questions']= final_outputs
        

        if torch.device=='cuda':
            torch.cuda.empty_cache()
        
        return output