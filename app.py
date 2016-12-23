#!/usr/bin/env python

import urllib
import json
import os

from flask import Flask
from flask import request
from flask import make_response

# Flask app should start in global layout
app = Flask(__name__)


@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)

    print("Request:")
    print(json.dumps(req, indent=4))

    res = processRequest(req)

    res = json.dumps(res, indent=4)
    # print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r


def processRequest(req):
    if req.get("result").get("action") != "cgmSgvDirection":
        return {}
    cgmurl = "https://logancgm.azurewebsites.net/api/v1/entries/sgv.json?count=1"
    result = urllib.urlopen(cgmurl).read()
    data = json.loads(result)
    res = makeWebhookResult(data)
    return res


def makeWebhookResult(data):
    if len(data) == 0:
        return {}
    
    sgv = data[0].get('sgv')
    if sgv is None:
        return {}

    direction = data[0].get('direction')
    if direction is None:
        return {}
        
    speech = "Sensor glucose value is currently " + str(sgv) + " with a direction of " + direction

    print("Response:")
    print(speech)

    return {
        "speech": speech,
        "displayText": speech,
        # "data": data,
        # "contextOut": [],
        "source": "apiai-cgm-webhook"
    }


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print "Starting app on port %d" % port

    app.run(debug=False, port=port, host='0.0.0.0')
