#nltk.download('brown')
#nltk.download('stopwords')
#nltk.download('popular')

import time
import torch
from transformers import T5ForConditionalGeneration,T5Tokenizer
import os
import numpy 
from Questgen.utilities import tokenize_sentences, get_keywords, get_sentences_for_keyword, \
                             generate_questions_mcq, generate_normal_questions


class QGen:
    
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
        
            
    def predict_mcq(self, payload):
        start = time.time()

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
   
        final_output = {}

        if len(keyword_sentence_mapping.keys()) == 0:
            return final_output
        else:
            try:
                generated_questions = generate_questions_mcq(keyword_sentence_mapping,self.device,self.tokenizer,self.model,self.s2v,self.normalized_levenshtein)

            except:
                return final_output
            end = time.time()

            final_output["statement"] = modified_text
            final_output["questions"] = generated_questions["questions"]
            final_output["time_taken"] = end-start
            
            if torch.device=='cuda':
                torch.cuda.empty_cache()
                
            return final_output
    
    def predict_shortq(self, payload):
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

        final_output = {}

        if len(keyword_sentence_mapping.keys()) == 0:
            print('ZERO')
            return final_output
        else:
            
            generated_questions = generate_normal_questions(keyword_sentence_mapping,self.device,self.tokenizer,self.model)
            
            
        final_output["statement"] = modified_text
        final_output["questions"] = generated_questions["questions"]
        
        if torch.device=='cuda':
            torch.cuda.empty_cache()

        return final_output
            
  
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

            
class AnswerPredictor:
          
    def __init__(self):
        self.tokenizer = T5Tokenizer.from_pretrained('t5-base')
        model = T5ForConditionalGeneration.from_pretrained(os.getcwd()+"/Questgen/models/answer_predictor")
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        model.to(device)
        # model.eval()
        self.device = device
        self.model = model
        self.set_seed(42)
        
    def set_seed(self,seed):
        numpy.random.seed(seed)
        torch.manual_seed(seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(seed)

    def greedy_decoding (inp_ids,attn_mask,model,tokenizer):
        greedy_output = model.generate(input_ids=inp_ids, attention_mask=attn_mask, max_length=256)
        Question =  tokenizer.decode(greedy_output[0], skip_special_tokens=True,clean_up_tokenization_spaces=True)
        return Question.strip().capitalize()

    def predict_answer(self,payload):
        start = time.time()
        inp = {
            "input_text": payload.get("input_text"),
            "input_question" : payload.get("input_question")
        }

        context = inp["input_text"]
        question = inp["input_question"]
        input = "question: %s <s> context: %s </s>" % (question,context)

        encoding = self.tokenizer.encode_plus(input, return_tensors="pt")
        input_ids, attention_masks = encoding["input_ids"].to(self.device), encoding["attention_mask"].to(self.device)
        greedy_output = self.model.generate(input_ids=input_ids, attention_mask=attention_masks, max_length=256)
        Question =  self.tokenizer.decode(greedy_output[0], skip_special_tokens=True,clean_up_tokenization_spaces=True)
        output = Question.strip().capitalize()

        return output
