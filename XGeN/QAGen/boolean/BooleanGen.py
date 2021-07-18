from typing import Set
import torch
from QAGen.utilities import tokenize_sentences

from QAGen.QGen import QGen


class BoolGen(QGen):
    
    def __init__(self, loader):
        QGen.__init__(self, loader)
        

    def predict_boolq(self, keywords, modified_text, full_keywords):
        sentences = tokenize_sentences(modified_text)
        
        keyword_sentence_mapping = self._QGen__get_sentences_for_keyword(keywords, sentences)     
        for k in keyword_sentence_mapping.keys():
            ks_len = len(keyword_sentence_mapping[k])
            text_snippet = " ".join(keyword_sentence_mapping[k][:min(3, ks_len)])
            keyword_sentence_mapping[k] = text_snippet

        if len(keyword_sentence_mapping.keys()) == 0:
            print('No keywords in this sentence')
            return []

        batch_text = []
        answers = keyword_sentence_mapping.keys()
        for answer in answers:
            txt = keyword_sentence_mapping[answer]
            text = "truefalse: %s passage: %s </s>" % (txt, True)
            batch_text.append(text)
        
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
        
        s = set()
        
        for index, val in enumerate(answers):
            out = outs[index, :]
            print(0)
            dec = self.tokenizer.decode(out, skip_special_tokens=True, clean_up_tokenization_spaces=True)
            if dec.find('Is there') == 0:
                continue

            print(1)
            answer = "Yes"
            correction = ""
            
            # Make a false question
            if(bool(self.rand.getrandbits(1)) and self._QGen__regex_search(dec, val)):
                option = self._QGen__find_alternative(val, full_keywords)
                answer = "No"
                correction = option + " -> " + val
                dec = self._QGen__replace_choice(dec, val, option)
            
            s.add((dec, answer, correction))
        
        if torch.device=='cuda':
            torch.cuda.empty_cache()
        
        #return output_array
        return list(s)
