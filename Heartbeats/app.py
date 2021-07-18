from flask import Flask, request
from threading import Thread
import uuid
import os
import time


app = Flask(__name__)


def back(x, y, z):
    print(x, y)
    f = open(z+'/test', 'w')
    f.close()
    time.sleep(60)
    os.rename(z+'/test', z+'/done')
    print('Done')


@app.route('/call', methods=['POST'])
def call():
    test = request.form.get('test')
    print(test)

    cur_uuid = uuid.uuid1()
    
    os.mkdir(str(cur_uuid))

    thread = Thread(target=back, args=(1, 2, str(cur_uuid)))
    thread.start()

    return {
        'Done': 1,
        'uuid': cur_uuid
    }

@app.route('/beats', methods=['POST'])
def beats():
    cur_uuid = request.form.get('uuid')

    status = 'Processing'
    data = None
    if os.path.exists(cur_uuid + '/done'):
        status = 'Finished'
        data = {
            '1': 1,
            '2': 2
        }

    resp = {
        'status': status
    }

    if data:
        resp['data'] = data

    return resp
