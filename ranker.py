

class Ranker:

    def __init__(self, keywords, phrases):
        self.keywords = []
        for k in keywords:
            self.keywords.append(k.lower())

        self.phrases = phrases
    
    def filter_phrases(self):
        filtered_phrases = {}
        
        for p in self.phrases:
            filtered_phrases[p] = []
            for k in self.keywords:
                if p.lower().find(k) != -1:
                    filtered_phrases[p].append(k)
            if len(filtered_phrases[p]) == 0:
                del filtered_phrases[p]

        return filtered_phrases
