from flask import Flask, request
from flask_ngrok import run_with_ngrok
from flask_cors import CORS
import os
import sys
import uuid

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


def download():
    import nltk
    nltk.download('punkt')
    nltk.download('brown')
    nltk.download('stopwords')
    nltk.download('popular')

def run():
    app.run()


def analyze_text(phrases, path):

    text = " ".join(phrases)

    keywords = topicExtract.extract_keywords(text)
    
    # TODO : Handle Async Ranker here
    phrase_topics = ranker.filter_phrases(keywords, phrases)

    # Save Paragraphs & Topics
    topicExtract.write_paragraphs_topics(phrase_topics, path)

    return keywords


@app.route("/api/upload/pdf", methods=['POST'])
def uploadPDF():
    file = request.files.get('file')
    start = int(request.form.get('start', 1))
    end = int(request.form.get('end', -1))

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
    preprocessor = PDFPreprocessor(directory_path, file_path, start, end)
    phrases = preprocessor.start_pipeline()
    
    # Process the text    
    keywords = analyze_text(phrases, directory_path + '/')
    
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
    preprocessor = TextPreprocessor()
    phrases = preprocessor.start_pipeline(text_payload)
    
    # Process the text    
    keywords = analyze_text(phrases, directory_path + '/')
    
    return {
        "uuid" : cur_uuid,
        "topics": keywords,
    }
    

@app.route("/api/examSpecifications", methods=['POST'])
def examSpecifications():
    cur_uuid = request.form.get('uuid')
    selected_topics = request.form.getlist('topics')
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
    
    # Load the user paragraphs & topics
    phrases = {}
    with open(directory_path + "/paragraph_topics.txt", 'r') as file:
        flag = 0
        phrase = ""
        while True:
            line = file.readline()
            if len(line) == 0:
                break
            
            if line == '#':
                flag = 0
            
            elif line == ';':
                flag = 1
            
            else:
                if flag == 0:
                    phrase += line

                else:
                    topics = list(filter(None, line.split(';')))

                    phrases[phrase] = topics
                    
                    # Add the new topics to the phrases
                    for keyword in selected_topics:
                        keyword = keyword.lower()
                        if keyword not in topics and phrase.lower().find(keyword) != -1:
                            phrases[phrase].insert(0,keyword)
                    
                    phrase = ""

            
    # Filter The paragraphs based on the selected topics
    filtered_phrases = ranker.rank_phrases(selected_topics, phrases)
    
    # Generate MCQ Questions
    i = 0
    count = mcq_count
    while(i < len(filtered_phrases) and i < count):
        mcq_questions += mcqGen.predict_mcq(filtered_phrases[i][1],filtered_phrases[i][0])
        i += 1
    # TODO : Filter Questions
    mcq_questions = ranker.random_questions(mcq_questions, mcq_count)
    print("Done MCQ")
    
    # Generate TF Questions
    count += tfq_count
    while(i < len(filtered_phrases) and i < count):
        tf_questions += tfGen.predict_tf(filtered_phrases[i][1],filtered_phrases[i][0])
        i += 1
    # TODO : Filter Questions
    tf_questions = ranker.random_questions(tf_questions, tfq_count)
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
    wh_questions = ranker.random_questions(wh_questions, whq_count)
    print("Done WH")
    
    # Generate Boolean Questions
    count += boolq_count
    while(i < len(filtered_phrases) and i < count):
        bool_questions += boolGen.predict_boolq(filtered_phrases[i][1],filtered_phrases[i][0])
        i += 1

    # TODO : Filter Questions
    bool_questions = ranker.random_questions(bool_questions, boolq_count)
    print("Done Boolean")    
    
    return {
        "wh_questions" : wh_questions,
        "bool_questions" : bool_questions,
        "tf_questions" : tf_questions,
        "mcq_questions" : mcq_questions, 
    }

if __name__ == '__main__':
    app.run()