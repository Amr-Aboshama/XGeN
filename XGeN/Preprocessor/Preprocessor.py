import cv2 as cv
import numpy as np
from pdf2image import convert_from_path
import os
from pytesseract import pytesseract
from PIL import Image
import spacy
import neuralcoref
import multiprocessing as mp
import time

class TextPreprocessor:

    def __init__(self):

        self.nlp = spacy.load('en_core_web_sm')
        neuralcoref.add_to_pipe(self.nlp)


    def __resolve_coreference(self, paragraphs):
        
        coref_paragraphs = []

        for p in paragraphs:
            doc = self.nlp(p)
            coref_paragraphs.append(doc._.coref_resolved)
        
        return coref_paragraphs


    def __pipeline_text(self, text):

        '''
        Pipeline:
            - Paragraph Segmentation + Clean Paragraphs
            - Resolve Coreference Resolution
        '''

        paragraphs = [p.replace('-\n', '').replace('\n', ' ') for p in text.split('\n\n') if len(p) >= 100]

        coref_paragraphs = self.__resolve_coreference(paragraphs)

        return coref_paragraphs


    def start_pipeline(self, text):
        
        text_paragraphs = self.__pipeline_text(text)

        return text_paragraphs




class PDFPreprocessor(TextPreprocessor):
   
    def __init__(self, working_path, pdf_path, start=1, end=-1):
        TextPreprocessor.__init__(self)

        self.pdf_path = pdf_path
        self.working_path = working_path
        self.start = start - 1
        
        if end != -1:
            if end <= start:
                self.end = self.start + 1
            else:
                self.end = end
        else:
            self.end = 1000000000

        self.tesseract_config = '''-c tessedit_char_whitelist=\\'\\"0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-()[];:,.!?/\\ '''
        
        # for windows
        #self.path_to_tesseract = r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
        # for linux
        self.path_to_tesseract = r"/usr/bin/tesseract"
        pytesseract.tesseract_cmd = self.path_to_tesseract
        

    def __convert_pdf_to_pages(self, path):

        pages = convert_from_path(self.pdf_path)

        os.mkdir(path)

        end = min(len(pages), self.end)


        for i in range(self.start, end):
            pages[i].save(path + '/'+str(i)+'.jpg', 'JPEG')


    def __remove_tables(self, gray):

        ret, bin_img = cv.threshold(gray,40,255,cv.THRESH_BINARY)
        major = cv.__version__.split('.')[0]
        if major == '3': img2, contours, hierarchy= cv.findContours(bin_img, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
        else: contours, hierarchy= cv.findContours(bin_img, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)


        width_threshold = 0.1 * gray.shape[1]
        for contour in contours:    
            [x,y, w, h] = cv.boundingRect(contour)
            if(w > width_threshold):
                gray[y:y+h, :] = 0
        
        return gray


    def __image_hist(self, binary):
        
        out = np.ones(binary.shape)
        out = out.astype(np.uint8)
        
        vec = []
        for y in range(binary.shape[0]):
            vec.append(np.sum(binary[y,:]))
        
        mn = 0.6 * np.max(vec)
        rng = 40
        lst = 0

        for y in range(len(vec)):
            if vec[y] >= mn:
                lst = y
            
            if np.abs(y-lst) <= rng:
                out[y] = np.copy(binary[y])

        lst = binary.shape[0]-1
        for y in range(len(vec)-1, -1, -1):
            if vec[y] >= mn:
                lst = y
            
            if np.abs(y-lst) <= rng:
                out[y] = np.copy(binary[y])
        
        return out


    def __image_crop(self, gray):

        left = 0
        right = 0

        vec = []
        for x in range(gray.shape[1]):
            vec.append(np.sum(gray[:,x]))
        

        mn = 0.5 * np.max(vec)
        margin = 20

        for x in range(gray.shape[1]):
            if vec[x] >= mn:
                left = x
                break

        for x in range(gray.shape[1]-1, -1, -1):
            if vec[x] >= mn:
                right = x
                break

        gray = gray[:,max(left-20, 0):min(right+20+1, gray.shape[1])]

        return 255 - gray 

    # Depricated
    def __extract_paragraph(self, gray):

        vec = []
        for y in range(gray.shape[0]):
            vec.append(np.sum(gray[y,:]))

        upper = 0.5 * max(vec)
        lower = 0.05 * max(vec)
        st = None
        ed = None

        upper_margin = 10
        margin = 15

        paragraphs = []

        for i in range(len(vec)):
            if vec[i] >= upper:
                if st is None:
                    st = i

            if st is not None and vec[i] > lower:
                ed = i

            if ed is not None and i-ed == 50:
                paragraphs.append(255-gray[max(st-margin, 0):min(ed+margin+1, len(vec)), :])
                st = None
                ed = None
        
        return paragraphs
        

    def __image_to_text(self, img):

        text = pytesseract.image_to_string(img, config=self.tesseract_config)
        return text


    def __pipeline_PDF(self, img_path):

        '''
        Pipeline:
            - Read Image
            - Convert to Binary
            - Remove Tables and borders
            - Improve by Histogram
            - Crop Interest zone
            - Convert Image to text
            - Remove Image
            - Paragraph Segmentation + Clean Paragraphs
            - Resolve Coreference Resolution
        '''

        img = cv.imread(img_path, cv.IMREAD_GRAYSCALE)

        # convert img to binary        
        bin_img = cv.threshold(img, 130, 255, cv.THRESH_BINARY_INV)[1]


        tableless_img = self.__remove_tables(bin_img)

        hist_img = self.__image_hist(tableless_img)

        crop_img = self.__image_crop(hist_img)

        text = self.__image_to_text(crop_img)[:-2]

        os.remove(img_path)

        return self._TextPreprocessor__pipeline_text(text)        
    

    def start_pipeline(self):
        
        path = self.working_path + '/images'

        self.__convert_pdf_to_pages(path)
        
        os.remove(self.pdf_path)

        imgs_names = os.listdir(path)

        pages_paragraphs = []

        for img_name in imgs_names:
            print('Started: ', img_name)
            pages_paragraphs += self.__pipeline_PDF(path + '/' + img_name)
            print('Finished: ', img_name)

        os.rmdir(path)

        return pages_paragraphs
