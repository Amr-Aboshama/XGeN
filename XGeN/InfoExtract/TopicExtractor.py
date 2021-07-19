from QAGen.utilities import tokenize_sentences, get_nouns_multipartite


class TopicExtractor:

    # def __init__(self, loader):
        # self.nlp = loader.nlp
        # self.s2v = loader.s2v
        # self.fdist = loader.fdist
        # self.normalized_levenshtein = loader.normalized_levenshtein

    # payload: {"phrase1":["topic1","topic2"], "phrase2":["topic1","topic3"]}
    def write_paragraphs_topics_json(self, payload, full_keywords):
        
        data = {
            'full_keywords' : [],
            'pairs' : []
        }

        for k in full_keywords:
            data['full_keywords'].append(k)

        
        for para, topic_list in payload.items():
            
            pair = {
                'paragraph': para,
                'topics': []
            }

            for topic in topic_list:
                pair['topics'].append(topic)
            
            data['pairs'].append(pair)
        
        return data

    def read_paragraphs_topics_json(self, paragraphs_topics, selected_topics):
        
        phrases = {}
        
        for pair in paragraphs_topics:
            phrase = pair['paragraph']
            topics =  pair['topics']
            phrases[phrase] = topics

            # Add the new topics to the phrases
            for keyword in selected_topics:
                keyword = keyword.lower()
                if keyword not in topics and phrase.lower().find(keyword) != -1:
                    phrases[phrase].insert(0,keyword)

        return phrases


    def extract_keywords(self, text, topics_num = 100):
        
        sentences = tokenize_sentences(text)
        joiner = " "
        modified_text = joiner.join(sentences)
        
        keywords = get_nouns_multipartite(modified_text, topics_num)
        
        return keywords
