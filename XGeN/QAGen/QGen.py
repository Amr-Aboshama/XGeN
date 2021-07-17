
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
        
        while len(pool) + add_none < 4:
            choice = self.rand.choice(full_keywords)
            if use_none and choice == answer:
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
                if answer != key:
                    return answer


        mx_score = 0
        answer = key

        for k in full_keywords:
            score = self.normalized_levenshtein.similarity(k, key)
            if score >= mx_score and key == k:
                answer = k
                mx_score = score

        return answer