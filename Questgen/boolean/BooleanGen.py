import re
import random
import torch
from Questgen.utilities import tokenize_sentences, get_keywords, get_sentences_for_keyword, \
                            get_options



class BoolGen:
       
    def __init__(self, base):
        self.tokenizer = base.tokenizer
        
        self.nlp = base.nlp
 
        self.s2v = base.s2v
        
        model = base.model
        device = base.device
        model.to(device)
        self.device = device
        self.model = model

        self.fdist = base.fdist
        self.normalized_levenshtein = base.normalized_levenshtein
        

    def predict_boolq(self,payload):
        text = payload.get("input_text")
        topics_num = payload.get('topics_num')

        sentences = tokenize_sentences(text)
        joiner = " "
        modified_text = joiner.join(sentences)
        
        keywords = get_keywords(self.nlp,modified_text,topics_num,self.s2v,self.fdist,self.normalized_levenshtein,len(sentences) )


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

        encoding = self.tokenizer.batch_encode_plus(batch_text, pad_to_max_length=True, return_tensors="pt")
        input_ids, attention_masks = encoding["input_ids"].to(self.device), encoding["attention_mask"].to(self.device)

        with torch.no_grad():
            outs = self.model.generate( input_ids=input_ids,
                                        attention_mask=attention_masks,
                                        max_length=256,
                                        num_beams=10,
                                        num_return_sequences=1,
                                        no_repeat_ngram_size=2,
                                        early_stopping=True
                                        )

        output_array ={}
        output_array["questions"] =[]
        
        for index, val in enumerate(answers):
            out = outs[index, :]
            dec = self.tokenizer.decode(out, skip_special_tokens=True, clean_up_tokenization_spaces=True)
            answer = "Yes, "
            correction = ""
            # Make a false question
            if(bool(random.getrandbits(1)) and dec.find(val) != -1):
                options = get_options(val, self.s2v)
                answer = "No, "
                correction = options[0][0] + " -> " + val
                dec = re.sub(re.escape(val), options[0][0], dec, flags=re.IGNORECASE)
            answer += keyword_sentence_mapping[val]
            output_array["questions"].append({"question": dec, "answer": answer, "correction": correction})
                    
        if torch.device=='cuda':
            torch.cuda.empty_cache()
        
        return output_array
    