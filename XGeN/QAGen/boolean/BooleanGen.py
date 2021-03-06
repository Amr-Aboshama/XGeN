import torch
from QAGen.QGen import QGen


class BoolGen(QGen):
    
    def __init__(self, loader):
        QGen.__init__(self, loader)


    def generate(self, keyword_sentence_mapping, full_keywords):
        '''
            Input: dictionary (keyword -> sentences), list of string (full keywords)
            Output: list of questions
            -------------------------------------------------------------------------
            Generate list of Boolean questions with answers.
        '''
        
        # Merge some related sentences to form a context.
        for k in keyword_sentence_mapping.keys():
            ks_len = len(keyword_sentence_mapping[k])
            text_snippet = " ".join(keyword_sentence_mapping[k][:min(3, ks_len)])
            keyword_sentence_mapping[k] = text_snippet

        if len(keyword_sentence_mapping.keys()) == 0:
            print('No keywords in this sentence')
            return []

        # Batch Queries Preparation
        batch_text = []
        answers = keyword_sentence_mapping.keys()
        for answer in answers:
            txt = keyword_sentence_mapping[answer]
            text = "truefalse: %s passage: %s </s>" % (txt, True)
            batch_text.append(text)
        
        # Encode Batch using T5 tokenizer
        encoding = self.tokenizer.batch_encode_plus(batch_text, pad_to_max_length=True, return_tensors="pt", max_length=512, truncation=True)
        # extract input_ids and attention masks of the batch
        input_ids, attention_masks = encoding["input_ids"].to(self.device), encoding["attention_mask"].to(self.device)
        
        with torch.no_grad():
            # Generate the questions
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
            # Decode the generated questions
            dec = self.tokenizer.decode(out, skip_special_tokens=True, clean_up_tokenization_spaces=True)
            if dec.find('Is there') == 0:
                continue

            print(1)
            answer = "Yes"
            correction = ""
            
            # Make a false question
            if(bool(self.rand.getrandbits(1)) and self._QGen__regex_search(dec, val)):
                option = self._QGen__find_alternative(dec, val, full_keywords)
                answer = "No"
                correction = option + " -> " + val
                dec = self._QGen__replace_choice(dec, val, option)
            
            s.add((dec, answer, correction))
        
        if torch.device=='cuda':
            torch.cuda.empty_cache()
        
        #return output_array
        return list(s)
