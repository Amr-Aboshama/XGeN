from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize
import string
import pke

class TopicExtractor:

    def __init__(self, rand):
        self.rand = rand
    

    def write_paragraphs_topics_json(self, payload, full_keywords):
        '''
            Input: Full_Keywords, dictionary of paragarph and keywords
            Output: Merged Dictionary of input data
            - Write full keywords of the document.
            - Write the extracted keywords with their paragraphs.
            - All are written to a json file to be read at exam specification request.  
        '''    

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
        '''
            Input: Dictionary of Paragraphs and Topics & Selected_Topics
            Output: Dictionary of phrases
            Read full keywords and the paragraphs with their related keywords from a json file
            to use in questions generation.
        '''

        phrases = {}
        
        for pair in paragraphs_topics:
            phrase = pair['paragraph']
            topics =  pair['topics']
            phrases[phrase] = topics

            # Add the new topics to the phrases
            for keyword in selected_topics:
                keyword = keyword.lower()
                if keyword not in topics and phrase.lower().find(keyword) != -1:
                    phrases[phrase].append(keyword)

            self.rand.shuffle(phrases[phrase])

        return phrases


    def get_nouns_multipartite(self, text, max_topics):
        '''
            Input: string (paragraphs), int (maximum topics number)
            Output: List of strings (keywords)
            Get documents keywords using:
            Multipartite Graph Based Keyphrase Extraction
        '''

        out = []

        extractor = pke.unsupervised.MultipartiteRank()
        extractor.load_document(input=text, language='en')
        pos = {'PROPN', 'NOUN'}
        stoplist = list(string.punctuation)
        stoplist += ['-lrb-', '-rrb-', '-lcb-', '-rcb-', '-lsb-', '-rsb-']
        stoplist += stopwords.words('english')
        extractor.candidate_selection(pos=pos, stoplist=stoplist)
        
        try:
            # Starting the clustering process
            extractor.candidate_weighting(alpha=1.1,
                                        threshold=0.74,
                                        method='average')
        except:
            return out

        keyphrases = extractor.get_n_best(n=max_topics)

        for key in keyphrases:
            out.append(key[0].lower())
        
        return out
        

    def tokenize_sentences(self, text):
        '''
            Input: string (paragraph)
            Output: List of strings (sentences)
            Sentence tokenization and cleaning
        '''

        sentences = sent_tokenize(text)
        
        # Remove any short sentences less than 20 letters.
        sentences = [sentence.strip() for sentence in sentences if len(sentence) > 20]
        return sentences


    def extract_keywords(self, text, topics_num = 100):
        '''
            Input: string (text paragraphs), int (maximum topics number)
            Output: List of strings (keywords)
            Extract top {topics_num} Keywords from the document
        '''

        sentences = self.tokenize_sentences(text)
        joiner = " "
        modified_text = joiner.join(sentences)
        
        keywords = self.get_nouns_multipartite(modified_text, topics_num)
        
        return keywords
