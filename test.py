import os
from pprint import pprint
from Questgen.Loader import Loader
from Questgen.QGen import QGen
from Questgen.mcq.MCQGen import MCQGen
from Questgen.boolean.BooleanGen import BoolGen
from Questgen.tf.TFGen import TFGen
from Questgen.shortq.ShortGen import ShortGen
from Questgen.longq.LongGen import LongGen
from Questgen.TopicExtractor import TopicExtractor

payload = {
            "input_text": "Sachin Ramesh Tendulkar is a former international cricketer from India and a former captain of the Indian national team. He is widely regarded as one of the greatest batsmen in the history of cricket. He is the highest run scorer of all time in International cricket.",
            "max_questions": 3,
            "topics_num": 3
          }

loader = Loader()
print("Done Loader")
qgen = QGen(Loader)
print("Done QGen")

def testTopicExtractor():
    directory = "test/"
    topicExtractor = TopicExtractor(loader)
    payload = {"paragraph1":["topic1","topic2"], "paragraph2":["topic1","topic3"]}
    if not os.path.exists(directory):
        os.makedirs(directory)
    topicExtractor.write_paragraphs_topics(payload, directory)

def testTF():
    tfGen = TFGen(qgen)
    output = tfGen.predict_tf(payload)
    pprint(output)

def testBoolean():
    boolGen = BoolGen(qgen)
    print("Done BoolGen")
    output = boolGen.predict_boolq(payload)
    pprint(output)

def testMCQ():
    mcqGen = MCQGen(qgen)
    output = mcqGen.predict_mcq(payload)
    pprint(output)

def testShortQ():
    shortGen = ShortGen(qgen)
    output = shortGen.predict_shortq(payload)
    pprint(output)

def testLongQ():
    longGen = LongGen(qgen)
    output = longGen.paraphrase(payload)
    pprint(output)




""" def testParaphrasing():
    qg = main.QGen(base)
    output = qg.paraphrase(payload)
    pprint(output)
    return output
 """

""" print("\nBoolean::")
testBoolean() """
""" print("\nTrue/False::")
testTF()
print("\nMCQ::")
testMCQ()
print("\nFAQ::")
testFAQ()


print("\nParaphrasing::")
out = testParaphrasing()

answer = main.AnswerPredictor()
payload3 = {
    "input_text" : out['Paragraph'],
    "input_question" : out['Paraphrased Questions'][0]
}
output = answer.predict_answer(payload3)
print(output)

 """
""" payload4 = {
    "input_text" : '''Sachin Ramesh Tendulkar is a former international cricketer from 
              India and a former captain of the Indian national team. He is widely regarded 
              as one of the greatest batsmen in the history of cricket. He is the highest
               run scorer of all time in International cricket.''',
    "input_question" : "Is Sachin tendulkar a former cricketer? "
}
output = answer.predict_answer(payload4)
print (output) """