from QAGen.utilities import tokenize_sentences, get_nouns_multipartite


class TopicExtractor:

    # def __init__(self, loader):
        # self.nlp = loader.nlp
        # self.s2v = loader.s2v
        # self.fdist = loader.fdist
        # self.normalized_levenshtein = loader.normalized_levenshtein

    # payload: {"phrase1":["topic1","topic2"], "phrase2":["topic1","topic3"]}
    def write_paragraphs_topics(self, payload, output_directory):
        
        with open(output_directory + 'paragraph_topics.txt', 'w+') as f:
            for para, topic_list in payload.items():
                f.write(para + '\n')
                for topic in topic_list:
                    f.write(topic + ';')
                f.write('\n')

    def extract_keywords(self, text, topics_num = 40):
        
        sentences = tokenize_sentences(text)
        # self.fdist = FreqDist(words_freq_dist(text))
        joiner = " "
        modified_text = joiner.join(sentences)
        
        keywords = get_nouns_multipartite(modified_text, topics_num)

        # keywords = get_keywords(self.nlp,modified_text,topics_num,self.s2v,self.fdist,self.normalized_levenshtein,len(sentences) )
        # keyword_sentence_mapping = get_sentences_for_keyword(keywords, sentences)

        # for k in keyword_sentence_mapping.keys():
        #     text_snippet = " ".join(keyword_sentence_mapping[k][:3])
        #     keyword_sentence_mapping[k] = text_snippet

        # return keyword_sentence_mapping, modified_text
        return keywords
