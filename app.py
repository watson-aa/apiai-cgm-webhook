#!/usr/bin/env python

import urllib
import json
import os
import datetime

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

    timezone = parameters.get("timezone")
    if timezone is None:
        timezone = 'America/Chicago'

    today = datetime.datetime.now()
    yesterday = today - datetime.timedelta(days=1)

    cgmUrl = {
        'sgv': cgmUrl + '/sgv.json?count=1',
        'sgvDir': cgmUrl + '/sgv.json?count=1',
        'sgvToday': cgmUrl + '/sgv.json?count=999&find[dateString][$gte]=' + today.strftime('%Y-%m-%d'),
        'sgvYesterday': cgmUrl + '/sgv.json?count=999&find[dateString][$gte]=' + yesterday.strftime('%Y-%m-%d') + '&find[dateString][$lt]=' + today.strftime('%Y-%m-%d'),
        'mbg': cgmUrl + '/mbg.json?count=1'
    }.get(entity, cgmUrl)

    result = urllib.urlopen(cgmUrl).read()
    data = json.loads(result)

    #print("Response:")
    #print(json.dumps(data, indent=4))

    res = makeWebhookResult(data, entity, timezone)
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
    }.get(direction, 'the direction is unknown')

def getSgvSpeech(data, withDirection=True):
    sgv = data[0].get('sgv')
    if sgv is None:
        return ''

    direction = data[0].get('direction')
    if direction is None:
        return ''

    speech = 'Sensor glucose value is currently ' + str(sgv)
    if withDirection == True:
        speech = speech + ' and ' + CGMdirectionToNL(direction) + '.'
    else:
        speech = speech + '.'

    return speech

def getSgvOutliers(data, timezone):
    minSgv = {'value': 0, 'date': datetime.datetime.now()}
    maxSgv = {'value': 0, 'date': datetime.datetime.now()}

    for d in data:
        tmpSvg = d.get('sgv')
        tmpDate = d.get('dateString')
        if tmpSvg is None or tmpDate is None:
            return ''
        if tmpSvg > maxSgv['value']:
            maxSgv['value'] = tmpSvg
            maxSgv['date'] = parse(tmpDate)
        if tmpSvg < minSgv['value'] or minSgv['value'] == 0:
            minSgv['value'] = tmpSvg
            minSgv['date'] = parse(tmpDate)

    return (minSgv, maxSgv)

def getSgvDaySpeech(day, minSgv, maxSgv):
    return day + ', the lowest sensor glucose value was ' +\
                str(minSgv['value']) + ' at ' + minSgv['date'].strftime('%I:%M%p') +\
                ', and the highest was ' + str(maxSgv['value']) +\
                ' at ' + maxSgv['date'].strftime('%I:%M%p') + '.'

def getSgvTodaySpeech(data, timezone):
    minSgv, maxSgv = getSgvOutliers(data, timezone)
    return getSgvDaySpeech('Today', minSgv, maxSgv)

def getSgvYesterdaySpeech(data, timezone):
    minSgv, maxSgv = getSgvOutliers(data, timezone)
    return getSgvDaySpeech('Yesterday', minSgv, maxSgv)

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

def makeWebhookResult(data, entity, timezone):
    if len(data) == 0:
        return {}

    speech = ''
    if entity == 'sgv':
        speech = getSgvSpeech(data, False)
    elif entity == 'sgvDir':
        speech = getSgvSpeech(data, True)
    elif entity == 'sgvToday':
        speech = getSgvTodaySpeech(data, timezone)
    elif entity == 'sgvYesterday':
        speech = getSgvYesterdaySpeech(data, timezone)
    elif entity == 'mbg':
        speech = getMbgSpeech(data)

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
