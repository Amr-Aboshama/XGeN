from QAGen.utilities import tokenize_sentences, get_nouns_multipartite


class TopicExtractor:

    # def __init__(self, loader):
        # self.nlp = loader.nlp
        # self.s2v = loader.s2v
        # self.fdist = loader.fdist
        # self.normalized_levenshtein = loader.normalized_levenshtein

    # payload: {"phrase1":["topic1","topic2"], "phrase2":["topic1","topic3"]}
    def write_paragraphs_topics(self, payload, full_keywords, output_directory):
        
        with open(output_directory + 'paragraph_topics.txt', 'w+') as f:

            for k in full_keywords:
                f.write(k + ';')
            f.write('\n')

            for para, topic_list in payload.items():
                f.write(para + '\n')
                for topic in topic_list:
                    f.write(topic + ';')
                f.write('\n')

    def extract_keywords(self, text, topics_num = 100):
        
        sentences = tokenize_sentences(text)
        joiner = " "
        modified_text = joiner.join(sentences)
        
        keywords = get_nouns_multipartite(modified_text, topics_num)
        
        return keywords
