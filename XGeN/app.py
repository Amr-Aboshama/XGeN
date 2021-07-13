from flask import Flask, request
from flask_ngrok import run_with_ngrok
import ast
from flask_cors import CORS
import os
import sys
import uuid

from XGeN.Preprocessor.preprocessor import Preprocessor
from XGeN.Preprocessor.utilities import solve_coreference, clean_text, word_segmentation, need_segmentation

from XGeN.InfoExtract.TopicExtractor import TopicExtractor

from XGeN.QAGen.Loader import Loader
from XGeN.QAGen.QGen import QGen
from XGeN.QAGen.mcq.MCQGen import MCQGen
from XGeN.QAGen.boolean.BooleanGen import BoolGen
from XGeN.QAGen.tf.TFGen import TFGen
from XGeN.QAGen.shortq.ShortGen import ShortGen
from XGeN.QAGen.longq.LongGen import LongGen
from XGeN.QAGen.anspred.AnswerPredictor import AnswerPredictor

from XGeN.Ranker.Ranker import filter_phrases, rank_phrases





# loader = Loader(os.getcwd()+"/XGeN/QAGen/models/s2v_old",
#                 os.getcwd()+"/XGeN/QAGen/models/question_generator",
#                 os.getcwd()+"/XGeN/QAGen/models/t5_boolean_questions".
#                 os.getcwd()+"/XGeN/QAGen/models/answer_predictor")


loader = Loader()

print("Done Loader")
qgen = QGen(loader)
print("Done QGen")

tfGen = TFGen(qgen)
print("Done TFGen")
boolGen = BoolGen(qgen)
print("Done BooleanGen")
mcqGen = MCQGen(qgen)
print("Done MCQGen")
shortGen = ShortGen(qgen)
print("Done ShortGen")
longGen = LongGen(qgen)
print("Done LongGen")
ansPredict = AnswerPredictor(loader)
print("Done AnswerPredictor")

topicExtract = TopicExtractor()
print("Done TopicExtractor")


if not os.path.exists('data'):
    os.mkdir('data')

app = Flask(__name__)
CORS(app)
run_with_ngrok(app)   


def download():
    import nltk
    nltk.download('punkt')
    nltk.download('brown')
    nltk.download('stopwords')
    nltk.download('popular')

def run():
    app.run()

def preprocess(phrase):
    phrase = clean_text(phrase)
    print('cleaned')
    if need_segmentation(phrase):
        print('need segmentation')
        phrase = word_segmentation(phrase)
        print('segmented')
    
    phrase = solve_coreference(phrase)
    print('coreferenced')
    
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


@app.route("/api/upload/pdf", methods=['POST'])
def uploadPDF():
    file = request.files.get('file')

    if file is None:
        return {
            "error": "No file uploaded!"
        }, 422

    cur_uuid = uuid.uuid1()
    # cur_uuid = uuid.UUID('9001a540-e1f0-11eb-92bf-0be814cdc50d')
        
    directory_path = 'data/' + str(cur_uuid)
    os.mkdir(directory_path)
    sys.setrecursionlimit(1500)
    
    file_path = directory_path + '/PDF.pdf'

    file.save(file_path)
    print('file saved!')

    # Handle Converting PDF to Text
    preprocessor = Preprocessor(file_path)
    phrases = []
    text = ""
    i = 1
    for page in preprocessor.page_by_page():
        page = preprocess(page)
        phrases.append(page)
        text += page + " "
        print(i)
        i += 1
    
    # Process the text    
    keywords = process(text, phrases, directory_path + '/')
    
    return {
        "uuid" : cur_uuid,
        "topics": keywords,
    }
    


@app.route("/api/upload/text", methods=['POST'])
def uploadText():
    text_payload = request.form.get('text')

    if text_payload is None:
        return {
            "error": "No text uploaded!"
        }, 422
    
    cur_uuid = uuid.uuid1()
    directory_path = 'data/' + str(cur_uuid)
    
    os.mkdir(directory_path)
    
    # Preprocess the text
    phrases = []
    text = ""
    for phrase in text_payload.split('\n\n'):
        #print(phrase)
        #print(text_payload.split('\n\n'))
        phrase = preprocess(phrase)
        text += " " + phrase
        phrases.append(phrase)

    # print(7)
    # # Process the text    
    keywords = process(text, phrases, directory_path + '/')
    # print(8)
    
    return {
        "uuid" : cur_uuid,
        "topics": keywords,
    }
    

@app.route("/api/examSpecifications", methods=['POST'])
def examSpecifications():
    cur_uuid = request.form.get('uuid')
    selected_topics = request.form.get('topics')
    whq_count = int(request.form.get('whq_count', 0))
    boolq_count = int(request.form.get('boolq_count', 0))
    tfq_count = int(request.form.get('tfq_count', 0))
    mcq_count = int(request.form.get('mcq_count', 0))

    directory_path = 'data/' + str(cur_uuid)

    wh_questions = []
    bool_questions = []
    tf_questions = []
    mcq_questions = []
    # Convert it from string to list
    #print(selected_topics)
    selected_topics = ast.literal_eval(selected_topics)
    #print(selected_topics)
    
    # Load the user paragraphs & topics
    phrases = {}
    with open(directory_path + "/paragraph_topics.txt", 'r') as file:
        while True:
            phrase = file.readline()
            if not phrase:
                break
            topics = file.readline().split(';')
            phrases[phrase] = topics

            # Add the new topics to the phrases
            for keyword in selected_topics:
                if keyword not in topics and phrase.lower().find(keyword) != -1:
                    phrases[phrase].append(keyword)
            
    # Filter The paragraphs based on the selected topics
    filtered_phrases = rank_phrases(selected_topics, phrases)
    
    # Generate MCQ Questions
    i = 0
    count = mcq_count
    while(i < len(filtered_phrases) and i < count):
        mcq_questions += mcqGen.predict_mcq(filtered_phrases[i][1],filtered_phrases[i][0])
        i += 1
    # TODO : Filter Questions
    print("Done MCQ")
    
    # Generate TF Questions
    count += tfq_count
    while(i < len(filtered_phrases) and i < count):
        tf_questions += tfGen.predict_tf(filtered_phrases[i][1],filtered_phrases[i][0])
        i += 1
    # TODO : Filter Questions
    print("Done TF")
    
    # Generate WH Questions
    count += whq_count
    while(i < len(filtered_phrases) and i < count):
        wh_questions += shortGen.predict_shortq(filtered_phrases[i][1],filtered_phrases[i][0])
        i += 1
        #if(i < len(filtered_phrases) and i < count):
        #    wh_questions += longGen.paraphrase(filtered_phrases[i][0])
        #    i += 1
    # TODO : Filter Questions
    print("Done WH")
    
    # Generate Boolean Questions
    count += boolq_count
    while(i < len(filtered_phrases) and i < count):
        bool_questions += boolGen.predict_boolq(filtered_phrases[i][1],filtered_phrases[i][0])
        i += 1
    # TODO : Filter Questions
    print("Done Boolean")    
    
    return {
        "wh_questions" : wh_questions,
        "bool_questions" : bool_questions,
        "tf_questions" : tf_questions,
        "mcq_questions" : mcq_questions, 
    }