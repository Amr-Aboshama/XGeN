from io import StringIO
from pdfminer.converter import TextConverter
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfpage import PDFPage

MAX_PAGES = 1500


class Preprocessor:
    def __init__(self):
        self.path = None
        self.pages = None
        self.start = 1
        self.end = MAX_PAGES

    def __read_pdf(self, path):
        try:
            file = open(path, 'rb')
            self.path = path
        except OSError:
            raise Exception("Can't open file: ", path)
        self.pages = PDFPage.get_pages(file, caching=True, check_extractable=True)

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
        self.set_start_page(1)
        self.set_end_page(MAX_PAGES)

        counter = 1
        for Page in self.page_by_page(path):
            if counter == page_number:
                return Page
            counter += 1
        return None


if __name__ == '__main__':
    preprocessor = Preprocessor()

    preprocessor.set_start_page(9)
    preprocessor.set_end_page(81)

    for page in preprocessor.page_by_page('inputs/modeling.pdf'):
        print(page)
        print()

    print("Finished")
