from flask import Flask, request
from flask_ngrok import run_with_ngrok
from flask_cors import CORS
import os
import sys
import uuid
import json
from threading import Thread

from Preprocessor.Preprocessor import TextPreprocessor, PDFPreprocessor

from InfoExtract.TopicExtractor import TopicExtractor

from QAGen.Loader import Loader
from QAGen.QGen import QGen
from QAGen.mcq.MCQGen import MCQGen
from QAGen.boolean.BooleanGen import BoolGen
from QAGen.tf.TFGen import TFGen
from QAGen.shortq.ShortGen import ShortGen
from QAGen.longq.LongGen import LongGen
from QAGen.anspred.AnswerPredictor import AnswerPredictor

from Ranker.Ranker import Ranker





# loader = Loader(os.getcwd()+"/XGeN/QAGen/models/s2v_old",
#                 os.getcwd()+"/XGeN/QAGen/models/question_generator",
#                 os.getcwd()+"/XGeN/QAGen/models/t5_boolean_questions".
#                 os.getcwd()+"/XGeN/QAGen/models/answer_predictor")


loader = Loader()
print("Done Loader")

qgen = QGen(loader)
print("Done QGen")

topicExtract = TopicExtractor()
print("Done TopicExtractor")

ranker = Ranker(loader.rand)
print("Done Ranker")

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




if not os.path.exists('data'):
    os.mkdir('data')

app = Flask(__name__)
CORS(app)
run_with_ngrok(app)

def writeJson(output_path, data):

    with open(output_path, 'w') as file:
        json.dump(data, file, indent=4)

def readJson(input_path):

    data = None

    with open(input_path, 'r') as file:
        data = json.load(file)
    
    return data

def download():
    import nltk
    nltk.download('punkt')
    nltk.download('brown')
    nltk.download('stopwords')
    nltk.download('popular')

def run():
    app.run()


def analyze_text(phrases, directory_path):

    text = " ".join(phrases)

    keywords_count = 40
    full_keywords = topicExtract.extract_keywords(text)
    full_count = len(full_keywords)
    
    keywords = full_keywords[:min(keywords_count, full_count)]

    # TODO : Handle Async Ranker here
    phrase_topics = ranker.filter_phrases(keywords, phrases)

    # Save Paragraphs & Topics
    topicExtract.write_paragraphs_topics(phrase_topics, full_keywords, directory_path + '/paragraph_topics.json')

    return keywords


def processUpload(directory_path, preprocessor, output_filename, text=None):

    phrases = None
    if text:
        phrases = preprocessor.start_pipeline(text)
    else:
        phrases = preprocessor.start_pipeline()


    # Process the text    
    keywords = analyze_text(phrases, directory_path)


    topics = {
        'topics': keywords
    }

    dummy_name = '/write.json'
    writeJson(directory_path + dummy_name, topics)

    os.rename(directory_path + dummy_name, directory_path + '/' + output_filename)
    

def processGenerateExam(cur_uuid, selected_topics, whq_count, boolq_count, tfq_count, mcq_count, output_filename):

    directory_path = 'data/' + str(cur_uuid)

    
    # Load the user paragraphs & topics
    phrases, full_keywords = topicExtract.read_paragraphs_topics(directory_path + "/paragraph_topics.json", selected_topics)
    
    # Filter The paragraphs based on the selected topics
    filtered_phrases = ranker.rank_phrases(selected_topics, phrases)
    
    counts = [mcq_count, tfq_count, whq_count, boolq_count]
    generators = [mcqGen, tfGen, shortGen, boolGen]
    questions = []

    for i in range(len(generators)):
        questions.append([])
        count = counts[i]
        while len(filtered_phrases) and count:
            q = generators[i].generate(filtered_phrases[0][1],filtered_phrases[0][0], full_keywords)
            filtered_phrases.pop(0)

            if not len(q):
                continue
            questions[-1] += q
            count -= 1
        
        # TODO : Filter Questions
        questions[-1] = ranker.random_questions(questions[-1], counts[i])
        print('Done Generator: ', i)

    
    quests = {
        "wh_questions" : questions[0],
        "bool_questions" : questions[1],
        "tf_questions" : questions[2],
        "mcq_questions" : questions[3], 
    }

    dummy_name = '/write2.json'
    writeJson(directory_path + dummy_name, quests)

    os.rename(directory_path + dummy_name, directory_path + '/' + output_filename)


@app.route("/api/upload/pdf", methods=['POST'])
def uploadPDF_API():
    file = request.files.get('file')
    start = int(request.form.get('start', 1))
    end = int(request.form.get('end', -1))

    if file is None:
        return {
            "error": "No file uploaded!"
        }, 422

    cur_uuid = uuid.uuid1()
        
    directory_path = 'data/' + str(cur_uuid)
    os.mkdir(directory_path)
    sys.setrecursionlimit(1500)
    
    file_path = directory_path + '/PDF.pdf'

    file.save(file_path)
    print('file saved!')

    # Handle Converting PDF to Text
    preprocessor = PDFPreprocessor(directory_path, file_path, start, end)

    output_filename = 'keywords.json'
    # Open back-thread for the preprocessor and information extraction
    Thread(target=processUpload, args=(directory_path, preprocessor, output_filename)).start()

    return {
        "status": 'Started',
        "filename": output_filename,
        "uuid" : cur_uuid,
    }


@app.route("/api/upload/text", methods=['POST'])
def uploadText_API():
    text_payload = request.form.get('text')

    if text_payload is None:
        return {
            "error": "No text uploaded!"
        }, 422
    
    cur_uuid = uuid.uuid1()
    directory_path = 'data/' + str(cur_uuid)
    
    os.mkdir(directory_path)
    
    # Preprocess the text
    preprocessor = TextPreprocessor()

    output_filename = 'keywords.json'
    # Open back-thread for the preprocessor and information extraction
    Thread(target=processUpload, args=(directory_path, preprocessor, output_filename, text_payload)).start()
    

    return {
        "status": 'Started',
        "filename": output_filename,
        "uuid" : cur_uuid,
    }
    

@app.route("/api/examSpecifications", methods=['POST'])
def examSpecifications_API():
    cur_uuid = request.form.get('uuid')
    selected_topics = request.form.getlist('topics')
    whq_count = int(request.form.get('whq_count', 0))
    boolq_count = int(request.form.get('boolq_count', 0))
    tfq_count = int(request.form.get('tfq_count', 0))
    mcq_count = int(request.form.get('mcq_count', 0))

    output_filename = 'questions.json'
    # Open back-thread for questions generation
    Thread(target=processGenerateExam, args=(cur_uuid, selected_topics, whq_count, boolq_count, tfq_count, mcq_count, output_filename)).start()

    return {
        "status": 'Started',
        "filename": output_filename
    }


@app.route('/api/heartbeat', methods=['POST'])
def heartbeat():
    cur_uuid = request.form.get('uuid')
    filename = request.form.get('filename')

    file_path = 'data/' + cur_uuid + '/' + filename

    response = {
        'status': 'Processing'
    }

    if os.path.exists(file_path):
        data = readJson(file_path)
        response['status'] = 'Finished'
        response['data'] = data

    return response, 200


if __name__ == '__main__':
    app.run()