import re

class QGen:
    
    def __init__(self, loader):
        
        self.nlp = loader.nlp
        self.s2v = loader.s2v
        self.fdist = loader.fdist
        self.normalized_levenshtein = loader.normalized_levenshtein
        self.rand = loader.rand
        
        self.tokenizer = loader.tokenizer
        self.device = loader.device

        self.qg_model = loader.qg_model
        self.bq_model = loader.bq_model
        self.ap_model = loader.ap_model

    
    def __get_options(self, answer, full_keywords, count = 4, none_exist = False):
    
        pool = set()
        
        use_none = self.rand.randint(0, 1)

        add_none = self.rand.randint(0, 1)
    
        if not none_exist:
            use_none = 0
            add_none = 0

        if not use_none:
            pool.add(answer)
        else:
            add_none = 1

        threshold = 0.55
        
        while len(pool) + add_none < 4:
            choice = self.rand.choice(full_keywords)
            score = self.normalized_levenshtein.similarity(choice, answer)
            if choice == answer or score > threshold:
                continue

            pool.add(choice)

        options = list(pool)

        self.rand.shuffle(options)

        if add_none:
            options.append('none of the above')

        ret_ans = answer

        if use_none:
            ret_ans = options[-1]

        return options, ret_ans

        

    def __find_alternative(self, key, full_keywords):

        use_near_false = self.rand.randint(0, 1)
        if not use_near_false:
            while True:

                answer = self.rand.choice(full_keywords)
                if answer.find(key) == -1 and key.find(answer) == -1:
                    return answer


        mx_score = 0
        answer = key
        threshold = 0.55

        for k in full_keywords:
            score = self.normalized_levenshtein.similarity(k, key)
            if score >= mx_score and score <= threshold and k.find(key) == -1 and key.find(k) == -1:
                answer = k
                mx_score = score

        return answer
    

    def __replace_choice(self, sentence, val, to_val = "____"):
        sentence
        esc_val = re.escape(val)
        sentence = re.sub(rf'([\s\'\"]){esc_val}([\s\'\"])', rf'\1{to_val}\2', sentence, flags=re.IGNORECASE)
        sentence = re.sub(rf'(\s){esc_val}([.,!?])', rf' {to_val}\2', sentence, flags=re.IGNORECASE)
        sentence = re.sub(rf'(^){esc_val}(\s)', rf'{to_val} ', sentence, flags=re.IGNORECASE)
        sentence = re.sub(rf'(\s){esc_val}($)', rf' {to_val}', sentence, flags=re.IGNORECASE)

        return sentence

    def __regex_search(self, sentence, word):
        esc_val = re.escape(word)

        count = 0
        count += len(re.findall(rf'([\s\'\"]){esc_val}([\s\'\"])', sentence, flags=re.IGNORECASE))
        count += len(re.findall(rf'(\s){esc_val}([.,!?])', sentence, flags=re.IGNORECASE))
        count += len(re.findall(rf'(^){esc_val}(\s)', sentence, flags=re.IGNORECASE))
        count += len(re.findall(rf'(\s){esc_val}($)', sentence, flags=re.IGNORECASE))

        return count