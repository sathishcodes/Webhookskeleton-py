#!/usr/bin/env python

import urllib
import json
import os
import nltk.classify.util
from nltk.classify import NaiveBayesClassifier
from nltk.corpus import names
import pickle
import logging
from textblob import TextBlob

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

    res = makeWebhookResult(req)

    res = json.dumps(res, indent=4)
    print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r

def word_feats(words):
    return dict([(word, True) for word in words])

def makeWebhookResult(req):
    action = req.get("result").get("action"); 
    
    feedback = req.get("resolvedQuery")
    
    result = req.get("result")
    parameters = result.get("parameters")
    portaltype = parameters.get("portal-types")
    
    DteTime = {'CS':'9 hours', 'PTO':'8 hours', 'Min': '40 hours', 'Due': 'Every Saturday'}
    #StaffitTime = {'CS':'8 hours', 'PTO':'8 hours'}
    
    if action == "tell.hours":        
        timetype = parameters.get("time-type")                
        
        speech = "You should book " + str(DteTime[timetype]) + " for " + timetype          
        
    elif action == "tell.minimumhours":
        speech = "You should minimum " + str(DteTime['Min']) + " each week"
    
    elif action == "tell.timeline":
        speech = portaltype + " is due on " + str(DteTime['Due'])
    
    elif action == "get.feedback.ask-feedback-custom":        
        speech = "Thanks for the feedback".
        
    return {
      "speech": speech,
      "displayText": speech,       
       # "contextOut": [],
       "source": "apiai-onlinestore-shipping"
    }

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print "Starting app on port %d" % port

    app.run(debug=True, port=port, host='0.0.0.0')
