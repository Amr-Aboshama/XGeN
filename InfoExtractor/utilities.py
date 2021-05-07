import string
import spacy

from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords

# nltk.download('wordnet')      #download if using this module for the first time
# nltk.download('stopwords')    #download if using this module for the first time

stopwords = set(stopwords.words('english'))
exclude = set(string.punctuation)
lemma = WordNetLemmatizer()
nlp = spacy.load('en_core_web_sm')


def clean(document):
    # remove the stopwords
    cleaned_document = " ".join([i for i in document.text.lower().split() if i not in stopwords])
    # remove the punctuations
    cleaned_document = ''.join(ch for ch in cleaned_document if ch not in exclude)
    normalized = " ".join(lemma.lemmatize(word) for word in cleaned_document.split())
    return normalized

def ner(text):
    nlp_text = nlp(text)
    out = {}
    for ent in nlp_text.ents:
        out[ent.text] = ent.label_
    return out

def pos(text):
    nlp_text = nlp(text)
    out = {}
    for word in nlp_text:
        out[word] = word.pos_
    return out