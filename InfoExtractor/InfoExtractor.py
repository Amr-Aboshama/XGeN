from utilities import clean
from collections import Counter

import spacy

nlp = spacy.load('en_core_web_sm')


class InfoExtractor:
    def __init__(self, book):
        self.book = book

    def bag_of_words(self):
        doc = nlp(self.book)
        compiled_doc = []
        # extract sentences using Spacy
        for sent in doc.sents:
            compiled_doc.append(sent)

        # remove punctuation,stopwords & lemmatize words
        final_doc = [clean(document).split() for document in compiled_doc]

        # flatten
        final_doc = [item for sublist in final_doc for item in sublist]
        words_bag = Counter(final_doc)
        return words_bag


if __name__ == '__main__':
    file = open('inputs/bag_of_words.txt', 'r')
    Book = file.read()

    info_extractor = InfoExtractor(Book)

    Bag = info_extractor.bag_of_words()
    print(Bag.most_common(10))
