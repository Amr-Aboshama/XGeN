import wordsegment
import spacy
import neuralcoref
import re as regex
# import nltk
# nltk.download('punkt')

from nltk.tokenize import sent_tokenize, word_tokenize
from wordsegment import load, segment

nlp = spacy.load('en_core_web_sm')
neuralcoref.add_to_pipe(nlp)
load()      # related to the wordsegment


def solve_coreference(paragraph):
    doc = nlp(paragraph)
    doc = doc._.coref_resolved
    #print(doc)
    return doc

def clean_text(text):
    sentences = sent_tokenize(text)
    clean_text = ""
    for sentence in sentences:
        # sentence.replace("•", " ")
        # sentence.replace("~", " ")
        # sentence.replace(",,", " ")
        sentence = regex.sub("~|•|,,", " ", sentence)
        #garbage = regex.search("~|,,", sentence)
        #if garbage:
        #    print("garbage: ", sentence)
        #else:
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
    
    average = 0
    if len(words):
        average = sum / len(words)
    return average > 10