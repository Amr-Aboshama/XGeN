import json

from QAGen.utilities import tokenize_sentences, get_nouns_multipartite


class TopicExtractor:

    # def __init__(self, loader):
        # self.nlp = loader.nlp
        # self.s2v = loader.s2v
        # self.fdist = loader.fdist
        # self.normalized_levenshtein = loader.normalized_levenshtein

    # payload: {"phrase1":["topic1","topic2"], "phrase2":["topic1","topic3"]}
    def write_paragraphs_topics(self, payload, full_keywords, output_path):
        
        with open(output_path, 'w') as f:

            for k in full_keywords:
                f.write(k + ';')
            f.write('\n')

            for para, topic_list in payload.items():
                f.write(para + '\n')
                for topic in topic_list:
                    f.write(topic + ';')
                f.write('\n')


    def read_paragraphs_topics(self, input_path, selected_topics):
        
        phrases = {}
        full_keywords = []
        
        with open(input_path, 'r') as file:
            
            line = file.readline()[:-1]
            
            if len(line):
                
                full_keywords = list(filter(None, line.split(';')))

                while True:
                    phrase = file.readline()
                    if len(phrase) == 0:
                        break
                    
                    phrase = phrase[:-1]

                    topics = file.readline()[:-1]
                    
                    topics = list(filter(None, topics.split(';')))

                    phrases[phrase] = topics
                            
                    # Add the new topics to the phrases
                    for keyword in selected_topics:
                        keyword = keyword.lower()
                        if keyword not in topics and phrase.lower().find(keyword) != -1:
                            phrases[phrase].insert(0,keyword)

        return phrases, full_keywords


    def write_topics(self, keywords, output_path):

        data = {
            'topics': keywords
        }

        with open(output_path, 'w') as file:
            json.dump(data, file, indent=4)


    def read_topics(self, input_path):

        data = None

        with open(input_path, 'w') as file:
            data = json.load(file)
        
        return data['topics']


    def extract_keywords(self, text, topics_num = 100):
        
        sentences = tokenize_sentences(text)
        joiner = " "
        modified_text = joiner.join(sentences)
        
        keywords = get_nouns_multipartite(modified_text, topics_num)
        
        return keywords
