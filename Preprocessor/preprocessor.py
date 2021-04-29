from io import StringIO
from pdfminer.converter import TextConverter
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfpage import PDFPage
from nltk.tokenize import sent_tokenize
from wordsegmentation import WordSegment

import spacy
import neuralcoref
import re as regex
# import nltk
# nltk.download('punkt')

nlp = spacy.load('en')
neuralcoref.add_to_pipe(nlp)

MAX_PAGES = 1500


class Preprocessor:
    def __init__(self):
        self.path = None
        self.pages = None
        self.start = 1
        self.end = MAX_PAGES
        self.paragraphs = None

    def __read_pdf(self, path):
        try:
            file = open(path, 'rb')
            self.path = path
        except OSError:
            raise Exception("Can't open file: ", path)
        self.pages = PDFPage.get_pages(file, caching=True, check_extractable=True)

    def read_text(self, path):
        try:
            file = open(path, 'r')
            self.path = path
        except OSError:
            raise Exception("Can't open file: ", path)
        text = file.read()
        self.paragraphs = text.split('\n\n')

    def solve_coreference(self, paragraph_number):
        if paragraph_number < 0 or paragraph_number >= len(self.paragraphs):
            raise Exception("Coreference: paragraph number out of range")
        doc = nlp(self.paragraphs[paragraph_number])
        self.paragraphs[paragraph_number] = doc._.coref_resolved
        return self.paragraphs[paragraph_number]

    def set_start_page(self, start):
        self.start = start

    def set_end_page(self, end):
        self.end = end

    def page_by_page(self, path):
        self.__read_pdf(path)

        counter = 0
        for Page in self.pages:
            # check the page limits
            counter += 1
            if counter < self.start or counter > self.end:
                continue
            # if counter > self.end:
            #     return None

            # create the needed objects to read the page
            resource_manager = PDFResourceManager()
            file_handler = StringIO()
            converter = TextConverter(resource_manager, file_handler)
            page_interpreter = PDFPageInterpreter(resource_manager, converter)

            # read the page and convert it to text
            page_interpreter.process_page(Page)
            text = file_handler.getvalue()

            # return the text and start from here in the next call
            yield text

            # close the opened handlers
            converter.close()
            file_handler.close()

    def get_page(self, path, page_number):
        self.set_start_page(page_number)
        self.set_end_page(page_number + 1)

        for Page in self.page_by_page(path):
            return Page

    def clean_text(self, text):
        sentences = sent_tokenize(text)
        clean_text = ""
        for sentence in sentences:
            garbage = regex.search("~|,,", sentence)
            if garbage:
                print("garbage: ", sentence)
            else:
                clean_text += sentence + " "
        return clean_text


if __name__ == '__main__':
    preprocessor = Preprocessor()

    # preprocessor.set_start_page(9)
    # preprocessor.set_end_page(81)
    # for page in preprocessor.page_by_page('inputs/modeling.pdf'):
    #     print(page)
    #     print()
    # print("Finished")

    # page = preprocessor.get_page('inputs/modeling.pdf', 23)
    # print(preprocessor.clean_text(page))

    preprocessor.read_text('inputs/coreference.txt')
    print("____________________________________________\n")
    for i in range(len(preprocessor.paragraphs)):
        paragraph = preprocessor.solve_coreference(i)
        print(paragraph)
        print()
