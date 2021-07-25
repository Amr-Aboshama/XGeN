
class Ranker:

    def __init__(self, rand):
        self.rand = rand
        
    #given all phreases and key words assign to each phrase the associated keywords
    # phrases: ["phrase1", "phrase2", ...]}
    def filter_phrases(self, keywords, phrases):
        filtered_phrases = {}
        
        for p in phrases:                           #loop on phrases
            filtered_phrases[p] = []
            
            self.rand.shuffle(keywords)             #for randoming
            for k in keywords:                      #loop on keywords
                if p.lower().find(k) != -1:         #if the phrase contain the keyword
                    filtered_phrases[p].append(k)   #assign the keyword to the phrase

            #eleminate phrases that have no associated keywords        
            if len(filtered_phrases[p]) == 0:
                del filtered_phrases[p]

        return filtered_phrases


    # given the phrases with their associated topics and the selected keywords by the user then outputs
    # only the phrases that are associated to keywords contained in the selected ones by the user
    # phrases: {"phrase1":["topic1","topic2"], "phrase2":["topic1","topic3"]}  

    def rank_phrases(self, selected_keywords, phrases):
        ranked_phrases = []
        
        for phrase in phrases:                          #loop on phrases-topics pairs
            topics = []
            for key in selected_keywords:               #loop on selected keywords
                if key in phrases[phrase]:              #if the selected keywoed is associated to the phrase
                    topics.append(key)                  #add the topic to associated ones
            ranked_phrases.append((phrase, topics))     #append the phrase and its selected keywords
        
        self.rand.shuffle(ranked_phrases)               #for randming

        return ranked_phrases                           

    
    #given the generated questions and required number of questions choose random questions(one type only) to create exam
    def random_questions(self, questions, number):
        final_questions = []
        
        while( len(questions) > 0 and len(final_questions) < number):
            q = self.rand.choice(questions)             #choose random question
            final_questions.append(q)                   #append it 
            questions.remove(q)                         #remove it in order not to be repeated
        
        return final_questions