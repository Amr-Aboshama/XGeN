from flask import Flask, request
import os
import uuid

from Preprocessor.preprocessor import Preprocessor
from Preprocessor.utilities import solve_coreference, clean_text, word_segmentation, need_segmentation

from InfoExtract.TopicExtractor import TopicExtractor

from QAGen.Loader import Loader
from QAGen.QGen import QGen
from QAGen.mcq.MCQGen import MCQGen
from QAGen.boolean.BooleanGen import BoolGen
from QAGen.tf.TFGen import TFGen
from QAGen.shortq.ShortGen import ShortGen
from QAGen.longq.LongGen import LongGen
from QAGen.anspred.AnswerPredictor import AnswerPredictor

from Ranker.Ranker import filter_phrases, rank_phrases


loader = Loader()
print("Done Loader")
qgen = QGen(Loader)
print("Done QGen")

tfGen = TFGen(qgen)
boolGen = BoolGen(qgen)
mcqGen = MCQGen(qgen)
shortGen = ShortGen(qgen)
longGen = LongGen(qgen)
ansPredict = AnswerPredictor(loader)

topicExtract = TopicExtractor(loader)


app = Flask(__name__)


def preprocess(phrase):
    phrase = clean_text(phrase)
    if need_segmentation(phrase):
        phrase = word_segmentation(phrase)
    phrase = solve_coreference(phrase)
    
    return phrase


def process(text, phrases, path):

    # TODO : Call the function to preprocess the text
    
    # TODO : Call Topic Extractor
    keywords = topicExtract.extract_keywords(text)
    
    # TODO : Handle Async Ranker here
    phrase_topics = filter_phrases(keywords, phrases)

    # Save Paragraphs & Topics
    topicExtract.write_paragraphs_topics(phrase_topics, path)

    return keywords


@app.route("/api/upload/PDF", methods=['POST'])
def uploadPDF():
    file = request.files.get('pdf')
    cur_uuid = uuid.uuid1()
    
    path = 'data/' + str(cur_uuid) + '/'
    os.mkdir(path)

    file.save(path + 'PDF.pdf')
    
    # Handle Converting PDF to Text
    preprocessor = Preprocessor()
    phrases = []
    text = ""
    for page in preprocessor.page_by_page('inputs/modeling.pdf'):
        page = preprocess(page)
        phrases.append(page)
        text += " " + page

    # Process the text    
    keywords = process(text, phrases, path)
    
    return {
        "uuid" : cur_uuid,
        "topics": keywords,
    }


@app.route("/api/upload/text", methods=['POST'])
def uploadText():
    text = request.form.get('text')
    cur_uuid = uuid.uuid1()
    
    path = 'data/' + str(cur_uuid) + '/'

    # Preprocess the text
    phrases = []
    text = ""
    for phrase in text.split('\n\n'):
        phrase = preprocess(phrase)
        text += " " + phrase

    # Process the text    
    keywords = process(text, phrases, path)
    
    return {
        "uuid" : cur_uuid,
        "topics": keywords,
    }

@app.route("/api/examSpecifications", methods=['POST'])
def examSpecifications():
    cur_uuid = request.form.get('uuid')
    selected_topics = request.form.getlist('topics')
    whq_count = request.form.get('whq_count')
    boolq_count = request.form.get('boolq_count')
    tfq_count = request.form.get('tfq_count')
    mcq_count = request.form.get('mcq_count')

    path = 'data/' + cur_uuid + '/'

    wh_questions = []
    bool_questions = []
    tf_questions = []
    mcq_questions = []

    # Load the user paragraphs & topics
    phrases = {}
    file = open(path + "paragraph_topics.txt", 'r')
    while True:
        phrase = file.readline()
        if not phrase:
            break
        topics = file.readline().split(';')
        phrases[phrase] = topics

    # Filter The paragraphs based on the selected topics
    filtered_phrases = rank_phrases(selected_topics, phrases)

    # Generate MCQ Questions
    i = 0
    count = mcq_count
    while(i < len(filtered_phrases) and i < count):
        mcq_questions.append(mcqGen.predict_mcq(filtered_phrases[i][1],filtered_phrases[i][0]))
        i += 1
    # TODO : Filter Questions
    
    # Generate TF Questions
    count += tfq_count
    while(i < len(filtered_phrases) and i < count):
        tf_questions.append(tfGen.predict_tf(filtered_phrases[i][1],filtered_phrases[i][0]))
        i += 1
    # TODO : Filter Questions

    # Generate Boolean Questions
    count += boolq_count
    while(i < len(filtered_phrases) and i < count):
        bool_questions.append(boolGen.predict_boolq(filtered_phrases[i][1],filtered_phrases[i][0]))
        i += 1
    # TODO : Filter Questions

    # Generate Boolean Questions
    count += whq_count
    while(i < len(filtered_phrases) and i < count):
        wh_questions.append(shortGen.predict_shortq(filtered_phrases[i][1],filtered_phrases[i][0]))
        wh_questions.append(longGen.paraphrase(filtered_phrases[i][0]))
        i += 1
    # TODO : Filter Questions

    return {
        "wh_questions" : wh_questions,
        "bool_questions" : bool_questions,
        "tf_questions" : tf_questions,
        "mc_questions" : mcq_questions, 
    }