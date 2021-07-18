# import random
from collections import OrderedDict
import string
import pke
from difflib import SequenceMatcher
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize, word_tokenize
from flashtext import KeywordProcessor

stopwords_set = set(stopwords.words('english'))
lemma = WordNetLemmatizer()

def MCQs_available(word,s2v):
    word = word.replace(" ", "_")
    sense = s2v.get_best_sense(word)
    if sense is not None:
        return True
    else:
        return False


def edits(word):
    "All edits that are one edit away from `word`."
    letters    = 'abcdefghijklmnopqrstuvwxyz '+string.punctuation
    splits     = [(word[:i], word[i:])    for i in range(len(word) + 1)]
    deletes    = [L + R[1:]               for L, R in splits if R]
    transposes = [L + R[1] + R[0] + R[2:] for L, R in splits if len(R)>1]
    replaces   = [L + c + R[1:]           for L, R in splits if R for c in letters]
    inserts    = [L + c + R               for L, R in splits for c in letters]
    return set(deletes + transposes + replaces + inserts)


def sense2vec_get_words(word,s2v):
    output = []

    word_preprocessed =  word.translate(word.maketrans("","", string.punctuation))
    word_preprocessed = word_preprocessed.lower()

    word_edits = edits(word_preprocessed)

    word = word.replace(" ", "_")

    sense = s2v.get_best_sense(word)
    most_similar = s2v.most_similar(sense, n=15)

    compare_list = [word_preprocessed]
    for each_word in most_similar:
        append_word = each_word[0].split("|")[0].replace("_", " ")
        append_word = append_word.strip()
        append_word_processed = append_word.lower()
        append_word_processed = append_word_processed.translate(append_word_processed.maketrans("","", string.punctuation))
        if append_word_processed not in compare_list and word_preprocessed not in append_word_processed and append_word_processed not in word_edits:
            output.append(append_word.title())
            compare_list.append(append_word_processed)


    out = list(OrderedDict.fromkeys(output))

    return out

def get_options(answer,s2v):
    distractors =[]

    try:
        # distractors = sense2vec_get_words(answer,s2v)
        
        if len(distractors) > 0:
            #print(" Sense2vec_distractors successful for word : ", answer)
            return distractors,"sense2vec"
    except:
        print (" Sense2vec_distractors failed for word : ",answer)


    return distractors,"None"


def tokenize_sentences(text):
    sentences = sent_tokenize(text)
    
    # Remove any short sentences less than 20 letters.
    sentences = [sentence.strip() for sentence in sentences if len(sentence) > 20]
    return sentences


def words_freq_dist(text):
    words_tokens = word_tokenize(text)
    words = [i.lower() for i in words_tokens if i.lower() not in stopwords_set]
    print(len(words), len(words_tokens))
    return words 


def is_far(words_list,currentword,thresh,normalized_levenshtein):
    threshold = thresh
    score_list =[]
    for word in words_list:
        score_list.append(normalized_levenshtein.distance(word.lower(),currentword.lower()))
    if min(score_list)>=threshold:
        return True
    else:
        return False

def filter_phrases(phrase_keys,max,normalized_levenshtein ):
    filtered_phrases =[]
    if len(phrase_keys)>0:
        filtered_phrases.append(phrase_keys[0])
        for ph in phrase_keys[1:]:
            if is_far(filtered_phrases,ph,0.7,normalized_levenshtein ):
                filtered_phrases.append(ph)
            if len(filtered_phrases)>=max:
                break
    return filtered_phrases


def get_nouns_multipartite(text, max_topics=40):
    out = []

    extractor = pke.unsupervised.MultipartiteRank()
    extractor.load_document(input=text, language='en')
    pos = {'PROPN', 'NOUN'}
    stoplist = list(string.punctuation)
    stoplist += ['-lrb-', '-rrb-', '-lcb-', '-rcb-', '-lsb-', '-rsb-']
    stoplist += stopwords.words('english')
    extractor.candidate_selection(pos=pos, stoplist=stoplist)
    # 4. build the Multipartite graph and rank candidates using random walk,
    #    alpha controls the weight adjustment mechanism, see TopicRank for
    #    threshold/method parameters.
    try:
        extractor.candidate_weighting(alpha=1.1,
                                      threshold=0.74,
                                      method='average')
    except:
        return out

    keyphrases = extractor.get_n_best(n=max_topics)

    for key in keyphrases:
        out.append(key[0].lower())
    
    return out


def get_phrases(doc):
    phrases={}
    for np in doc.noun_chunks:
        phrase =np.text
        len_phrase = len(phrase.split())
        if len_phrase > 1:
            if phrase not in phrases:
                phrases[phrase]=1
            else:
                phrases[phrase]=phrases[phrase]+1

    phrase_keys=list(phrases.keys())
    phrase_keys = sorted(phrase_keys, key= lambda x: len(x),reverse=True)
    phrase_keys=phrase_keys[:50]
    return phrase_keys



def get_keywords(nlp,text,max_keywords,s2v,fdist,normalized_levenshtein,no_of_sentences):
    doc = nlp(text)
    max_keywords = int(max_keywords)

    keywords = get_nouns_multipartite(text)
    
    keywords = sorted(keywords, key=lambda x: fdist[x])
    
    keywords = filter_phrases(keywords, max_keywords,normalized_levenshtein )

    phrase_keys = get_phrases(doc)
    filtered_phrases = filter_phrases(phrase_keys, max_keywords,normalized_levenshtein )

    total_phrases = keywords + filtered_phrases

    total_phrases_filtered = filter_phrases(total_phrases, min(max_keywords, 2*no_of_sentences),normalized_levenshtein )


    answers = []
    for answer in total_phrases_filtered:
        if answer not in answers and MCQs_available(answer,s2v):
            answers.append(answer)

    answers = answers[:max_keywords]
    return answers


def random_choice(rand):
    a = rand.choice([0,1])
    return bool(a)
    

def find_alternative(key, s2v, normalized_levenshtein, rand):
    options, _ = get_options(key, s2v)
    # options =  filter_phrases(options, 10, normalized_levenshtein)

    while(len(options) > 0):
        option = rand.choice(options)
        if SequenceMatcher(None, option.lower(), key.lower()).ratio() < 0.7:
            return option
        options.remove(option)
    #if len(options[0]):
    #    option = options[0][0]
        # Note: The next line may cause an infinite loop
        #while SequenceMatcher(None, option.lower(), key.lower()).ratio() > 0.7:
        #    print(option, key, SequenceMatcher(None, option, key).ratio())
        #    option = rand.choice(options[0])
    #for option in options[0]:
    #    if SequenceMatcher(None, option.lower(), key.lower()).ratio() < 0.7:
    #        #print(option, key, SequenceMatcher(None, option, key).ratio())
    #        return option
    return key