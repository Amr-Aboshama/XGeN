
class Ranker:

    def __init__(self, rand):
        self.rand = rand
        
    # phrases: ["phrase1", "phrase2", ...]}
    def filter_phrases(self, keywords, phrases):
        filtered_phrases = {}
        
        for p in phrases:
            filtered_phrases[p] = []
            
            self.rand.shuffle(keywords)
            for k in keywords:
                if p.lower().find(k) != -1:
                    filtered_phrases[p].append(k)
                    
            if len(filtered_phrases[p]) == 0:
                del filtered_phrases[p]

        return filtered_phrases

    # phrases: {"phrase1":["topic1","topic2"], "phrase2":["topic1","topic3"]}
    # TODO : Rank based on the frequent topics   
    def rank_phrases(self, selected_keywords, phrases):
        ranked_phrases = []
        
        for phrase in phrases:
            topics = []
            for key in selected_keywords:
                if key in phrases[phrase]:
                    topics.append(key)
            ranked_phrases.append((phrase, topics))
        
        self.rand.shuffle(ranked_phrases)

        return ranked_phrases

    def random_questions(self, questions, number):
        final_questions = []
        
        while( len(questions) > 0 and len(final_questions) < number):
            q = self.rand.choice(questions)
            final_questions.append(q)
            questions.remove(q)
        
        return final_questions