#!/usr/bin/env python

import urllib
import json
import os
from dateutil.parser import parse

from flask import Flask
from flask import request
from flask import make_response

# Flask app should start in global layout
app = Flask(__name__)


@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)

    #print("Request:")
    #print(json.dumps(req, indent=4))

    res = processRequest(req)

    res = json.dumps(res, indent=4)
    # print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r


def processRequest(req):
    if req.get("result").get("action") != "cgm":
        return {}

    parameters = req.get("result").get("parameters")
    if parameters is None:
        return {}

    cgmUrl = parameters.get("cgmUrl")
    if cgmUrl is None:
        return {}

    entity = parameters.get("entity")
    if entity is None:
        return {}

    cgmUrl = {
        'sgv': cgmUrl + '/sgv.json?count=1',
        'sgvDir': cgmUrl + '/sgv.json?count=1',
        'mbg': cgmUrl + '/mbg.json?count=1'
    }.get(entity, cgmUrl)

    result = urllib.urlopen(cgmUrl).read()
    data = json.loads(result)

    #print("Response:")
    #print(json.dumps(data, indent=4))

    res = makeWebhookResult(data, entity)
    return res

def CGMdirectionToNL(direction):
    return {
        'SingleDown': 'dropping',
        'DoubleDown': 'dropping rapidly',
        'FortyFiveDown': 'dropping slightly',
        'FortyFiveUp': 'rising slightly',
        'SingleUp': 'rising',
        'DoubleUp': 'rising rapidly',
        'Flat': 'flat'
    }.get(direction, 'unknown')

def getSgvDirSpeech(data):
    sgv = data[0].get('sgv')
    if sgv is None:
        return ''

    direction = data[0].get('direction')
    if direction is None:
        return ''

    return 'Sensor glucose value is currently ' + str(sgv) + ' and ' + CGMdirectionToNL(direction) + '.'

def getMbgSpeech(data):
    mbg = data[0].get('mbg')
    print 'MBG:' + str(mbg)
    if mbg is None:
        return ''

    date = data[0].get('dateString')
    if date is None:
        return ''
    date_obj = parse(date)
    date_str = date_obj.strftime('%B %d at %I:%M%p')

    return 'Mean blood glucose value was ' + str(mbg) + ' on ' + date_str + '.'

def makeWebhookResult(data, entity):
    if len(data) == 0:
        return {}

    speech = {
        'sgvDir': getSgvDirSpeech(data),
        'mbg': getMbgSpeech(data)
    }.get(entity, '')
    if speech == '':
        return {}

    return {
        "speech": speech,
        "displayText": speech,
        "source": "apiai-cgm-webhook"
    }


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print "Starting app on port %d" % port

    app.run(debug=False, port=port, host='0.0.0.0')
