

class Ranker:

    def __init__(self, keywords, phrases):
        self.keywords = []
        for k in keywords:
            self.keywords.append(k.lower())

        self.phrases = phrases
    
    def filter_phrases(self):
        filtered_phrases = []
        
        for p in self.phrases:
            for k in self.keywords:
                if p.lower().find(k):
                    filtered_phrases.append(p)
                    break

        return filtered_phrases
