import wordsegment
import spacy
import neuralcoref
import re as regex
# import nltk
# nltk.download('punkt')

from nltk.tokenize import sent_tokenize, word_tokenize
from wordsegment import load, segment

nlp = spacy.load('en')
neuralcoref.add_to_pipe(nlp)
load()      # related to the wordsegment


def solve_coreference(paragraph):
    doc = nlp(paragraph)
    return doc

def clean_text(text):
    sentences = sent_tokenize(text)
    clean_text = ""
    for sentence in sentences:
        garbage = regex.search("~|,,", sentence)
        if garbage:
            print("garbage: ", sentence)
        else:
            clean_text += sentence + " "
    return clean_text

def word_segmentation(paragraph):
    output = ""
    for sentence in sent_tokenize(paragraph):
        words = segment(sentence)
        sentence = ""
        for word in words:
            sentence += word + " "
        output += sentence[:-1] + ". "
    return output
    
def need_segmentation(paragraph):
    words = word_tokenize(paragraph)
    sum = 0
    for word in words:
        sum += len(word)
    average = sum / len(words)
    return average > 10