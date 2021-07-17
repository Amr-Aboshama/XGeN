import re
# import random
from typing import Set
import torch
from QAGen.utilities import tokenize_sentences, get_sentences_for_keyword

from QAGen.QGen import QGen


class BoolGen(QGen):
    
    def __init__(self, loader):
        QGen.__init__(self, loader)
        

    def predict_boolq(self, keywords, modified_text, full_keywords):
        sentences = tokenize_sentences(modified_text)
        
        keyword_sentence_mapping = get_sentences_for_keyword(keywords, sentences)     
        for k in keyword_sentence_mapping.keys():
            text_snippet = " ".join(keyword_sentence_mapping[k][:3])
            keyword_sentence_mapping[k] = text_snippet

        batch_text = []
        answers = keyword_sentence_mapping.keys()
        for answer in answers:
            txt = keyword_sentence_mapping[answer]
            text = "truefalse: %s passage: %s </s>" % (txt, True)
            batch_text.append(text)
        
        if len(batch_text) == 0:
            return []
        encoding = self.tokenizer.batch_encode_plus(batch_text, pad_to_max_length=True, return_tensors="pt", max_length=512, truncation=True)
        input_ids, attention_masks = encoding["input_ids"].to(self.device), encoding["attention_mask"].to(self.device)
        
        with torch.no_grad():
            outs = self.bq_model.generate( input_ids=input_ids,
                                        attention_mask=attention_masks,
                                        max_length=256,
                                        num_beams=10,
                                        num_return_sequences=1,
                                        no_repeat_ngram_size=2,
                                        early_stopping=True
                                        )
        #output_array = []
        #output_array["questions"] =[]
        
        for index, val in enumerate(answers):
            out = outs[index, :]
            print(0)
            dec = self.tokenizer.decode(out, skip_special_tokens=True, clean_up_tokenization_spaces=True)
            print(1)
            s = set()
            answer = "Yes"
            correction = ""
            
            # Make a false question
            if(bool(self.rand.getrandbits(1)) and dec.find(val) != -1):
                option = self._QGen__find_alternative(val, full_keywords)
                answer = "No"
                correction = option + " -> " + val
                dec = re.sub(re.escape(val), option, dec, flags=re.IGNORECASE)
            
            s.add((dec, answer, correction))
        
        if torch.device=='cuda':
            torch.cuda.empty_cache()
        
        #return output_array
        return list(s)
