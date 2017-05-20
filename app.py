#!/usr/bin/env python

import urllib
import json
import os
import pyrebase
import firebase_admin

from firebase_admin import credentials
from textblob import TextBlob
from flask import Flask
from flask import request
from flask import make_response

# Flask app should start in global layout
app = Flask(__name__)

config = {
  "apiKey": "AIzaSyDR_gxQXRxaGkM9YXEcFYy14mN_zh5HG4s",
  "authDomain": "buddywiser-b7238.firebaseapp.com",
  "databaseURL": "https://buddywiser-b7238.firebaseio.com",
  "storageBucket": "buddywiser-b7238.appspot.com",
  "serviceAccount" : "buddywiser-b7238-firebase-adminsdk-p0m7z-d5ed363a78.json"
}

firebase = pyrebase.initialize_app(config)
# auth = firebase.auth()
# user = auth.sign_in_with_email_and_password("buddydev101@gmail.com", "Analytics2017")
db = firebase.database()
# feedbackRef = db.child("feedbacks")


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
    action = req.get("result").get("action")
    result = req.get("result")
    parameters = result.get("parameters")
    portaltype = parameters.get("portal-types")
    
    DteTime = {'CS':'9 hours', 'PTO':'8 hours', 'Min': '40 hours', 'Due': 'Every Saturday'}
    #StaffitTime = {'CS':'8 hours', 'PTO':'8 hours'}
    
    if db.child("feedbacks").child("feedbackTriggered").get().val() == 1: # if feedback intent has been triggered previously 
                                                                          # then treat the incoming intest as feedback
        feedback = result.get("resolvedQuery");    
        fb_str = str(feedback)        
        blob = TextBlob(fb_str)                       
        db.child("feedbacks").child("dte").child("messages").push(feedback)
        if  blob.sentiment.polarity > 0:
            speech = "Glad to hear that! Thanks for the feedback :) "
            posCount = db.child("feedbacks").child("dte").child("positiveCount").get().val() + 1;
            db.child("feedbacks").child("dte").child("positiveCount").set(posCount)
        else:
            speech = "Sorry to hear that! Thanks for the feedback :) "
            negCount = db.child("feedbacks").child("dte").child("negetiveCount").get().val() + 1;
            db.child("feedbacks").child("dte").child("negetiveCount").set(negCount)

        db.child("feedbacks").child("feedbackTriggered").set(0) # reset the feedback flag

    elif action == "tell.hours":        
        timetype = parameters.get("time-type")                
        
        speech = "You should book " + str(DteTime[timetype]) + " for " + timetype          

        db.child("feedbacks").child("feedbackTriggered").set(0) # reset the feedback flag
        
    elif action == "tell.minimumhours":
        speech = "You should minimum " + str(DteTime['Min']) + " each week"

        db.child("feedbacks").child("feedbackTriggered").set(0) # reset the feedback flag
    
    elif action == "tell.timeline":
        if portaltype == "Check-ins":
          speech = portaltype + "should be done bi-weekly"
        else:
          speech = portaltype + " is due on " + str(DteTime['Due'])

        db.child("feedbacks").child("feedbackTriggered").set(0) # reset the feedback flag
    
    elif action == "get.feedback.ask-feedback-custom":            
        feedback = result.get("resolvedQuery");    
        fb_str = str(feedback)        
        blob = TextBlob(fb_str)                       
        db.child("feedbacks").child("dte").child("messages").push(feedback)
        if  blob.sentiment.polarity > 0:
            speech = "Glad to hear that! Thanks for the feedback :) "
            posCount = db.child("feedbacks").child("dte").child("positiveCount").get().val() + 1;
            db.child("feedbacks").child("dte").child("positiveCount").set(posCount)
        else:
            speech = "Sorry to hear that! Thanks for the feedback :) "
            negCount = db.child("feedbacks").child("dte").child("negetiveCount").get().val() + 1;
            db.child("feedbacks").child("dte").child("negetiveCount").set(negCount)

        db.child("feedbacks").child("feedbackTriggered").set(0) # reset the feedback flag

    elif action == "input.unknown":
         db.child("feedbacks").child("feedbackTriggered").set(0) # reset the feedback flag        
        
    elif action == "get.feedback":
          db.child("feedbacks").child("feedbackTriggered").set(1) # set the feedback flag
                    
    return {
      "speech": speech,
      "displayText": speech,             
       # "contextOut": [],
       "source": " "
    }

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    # print "Starting app on port %d" % port

    app.run(debug=True, port=port, host='0.0.0.0')
