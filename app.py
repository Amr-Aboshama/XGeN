from flask import Flask, request
import os
import uuid

from QAGen.Loader import Loader
from QAGen.QGen import QGen
from QAGen.mcq.MCQGen import MCQGen
from QAGen.boolean.BooleanGen import BoolGen
from QAGen.tf.TFGen import TFGen
from QAGen.shortq.ShortGen import ShortGen
from QAGen.longq.LongGen import LongGen
from InfoExtract.TopicExtractor import TopicExtractor
from QAGen.anspred.AnswerPredictor import AnswerPredictor
from Ranker.Ranker import Ranker

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


@app.route("/api/upload/PDF", methods['POST'])
def uploadPDF():
    file = request.files.get('pdf')
    cur_uuid = uuid.uuid1()
    topics = []

    # TODO : Handle Converting PDF to Text

    # TODO : Call the function to preprocess the text
    
    # TODO : Call Topic Extractor

    # TODO : Handle Async Ranker here

    return {
        "uuid" : cur_uuid,
        "topics": topics,
    }


@app.route("/api/upload/text", methods['POST'])
def uploadText():
    text = request.form.get('text')
    cur_uuid = uuid.uuid1()
    topics = []

    # TODO : Call the function to preprocess the text

    # TODO : Call Topic Extractor

    # TODO : Handle Async Ranker here

    return {
        "uuid" : cur_uuid,
        "topics": topics,
    }

@app.route("/api/examSpecifications", methods['POST'])
def examSpecifications():
    cur_uuid = request.form.get('uuid')
    selected_topics = request.form.getlist('topics')
    whq_count = request.form.get('whq_count')
    boolq_count = request.form.get('boolq_count')
    tfq_count = request.form.get('tfq_count')
    mcq_count = request.form.get('mcq_count')

    wh_questions = []
    bool_questions = []
    tf_questions = []
    mc_questions = []

    # TODO : Get the questions


    return {
        "wh_questions" : wh_questions,
        "bool_questions" : bool_questions,
        "tf_questions" : tf_questions,
        "mc_questions" : mc_questions, 
    }