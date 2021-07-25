
class AnswerPredictor:
          
    def __init__(self, loader):
        self.tokenizer = loader.tokenizer
        self.device = loader.device
        self.model = loader.qg_model


    def predict_answer(self,payload):
        '''
            Input: Dictionary has question and context
            Output: string (predicted answer)
            -------------------------------------------------------------
            Predict the answer of the question in some context using fine-tuned t5 transformer
        '''
        input = "question: %s <s> context: %s </s>" % (payload["question"], payload["context"])

        # Encode Input using t5 tokenizer.
        encoding = self.tokenizer.encode_plus(input, return_tensors="pt")
        # get the ids of the input and their attention mask.
        input_ids, attention_masks = encoding["input_ids"].to(self.device), encoding["attention_mask"].to(self.device)
        # Generate encoded output using a T5 pretrained model.
        greedy_output = self.model.generate(input_ids=input_ids, attention_mask=attention_masks, max_length=256)
        # Decode Output using t5 tokenizer.
        Question =  self.tokenizer.decode(greedy_output[0], skip_special_tokens=True,clean_up_tokenization_spaces=True)
        # Modify Output.
        output = Question.strip().capitalize()

        return output