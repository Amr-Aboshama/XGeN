
class AnswerPredictor:
          
    def __init__(self, loader):
        self.tokenizer = loader.tokenizer
        self.device = loader.device
        self.model = loader.qg_model


    def predict_answer(self,payload):
        
        input = "question: %s <s> context: %s </s>" % (payload["question"], payload["context"])

        encoding = self.tokenizer.encode_plus(input, return_tensors="pt")
        input_ids, attention_masks = encoding["input_ids"].to(self.device), encoding["attention_mask"].to(self.device)
        greedy_output = self.model.generate(input_ids=input_ids, attention_mask=attention_masks, max_length=256)
        Question =  self.tokenizer.decode(greedy_output[0], skip_special_tokens=True,clean_up_tokenization_spaces=True)
        output = Question.strip().capitalize()

        return output