import requests
import os
from flask import Flask, request, session, redirect, render_template, Response, make_response, jsonify
from flask_ask import (
    Ask,
    request as ask_request,
    session as ask_session,
    context as ask_context,
    version, question, statement, audio, current_stream
)
import logging
import urllib

app = Flask(__name__)
ask = Ask(app, '/')
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
logging.getLogger('flask_ask').setLevel(logging.DEBUG)

# Helper Methods
def sessionInfo():
    logging.info("User ID: {}".format(ask_session.user.userId))
    #logging.info("Access token: {}".format(ask_session.user.accessToken))

    #logging.info("Device ID: {}".format(ask_context.System.device.deviceId))
    #logging.info("API endpoint: {}".format(ask_context.System.device.deviceId))
    #logging.info("Consent Token: {}".format(ask_context.System.apiEndpoint))
    #return str(ask_session.user.userId), str(ask_context.System.device.deviceId), str(ask_context.System.user.permissions.consentToken), str(ask_context.System.apiEndpoint)


def getUser(token):
    api = "https://api.amazon.com/user/profile?access_token="+str(token)
    r = requests.get(api)
    user = r.json()
    #print user
    if r.status_code == 200:
        return user['name'], user['email'], user['user_id']
    else: 
        print "profile error"
        return None


def haveibeenpwned(email):
    headers = {"api-version":2, "User-Agent":"alexa-nealrs"}
    api = "https://haveibeenpwned.com/api/v2/breachedaccount/"+email+"?includeUnverified=true"
    r = requests.get(api, headers=headers)
    #print api
    #print r.status_code
    #breaches = r.json()
    #print breaches
    if r.status_code == 200:
        breaches=[]
        for b in r.json():
            #print b['Name']
            breaches.append(b['Title'] + " in "+ b['BreachDate'][:4])
        #print breaches
        return breaches
    else: 
        print "haveibeenpwned API error"
        return None


def oxford_comma_join(l):
    if not l:
        return ""
    elif len(l) == 1:
        return l[0]
    else:
        return ', '.join(l[:-1]) + ", and " + l[-1]



@app.route("/", methods=["GET", "POST"])
def home():
    return render_template('privacy.html')

# Alexa Intents
@ask.launch
@ask.default_intent
@ask.intent('mainIntent')
def launch():
    print "skill launch"
    sessionInfo()
    if ask_session.user.accessToken is None:
        speech = "Welcome to Hack Me. Please open the Alexa app to link this Skill with your Amazon account. This will enable us to check your email address against the Have I been powned database. We will not store, sell, or give away your email address."
        return statement(speech).link_account_card()
    else:
        name, email, userId  = getUser(ask_session.user.accessToken)
        breaches = haveibeenpwned(str(email))
        #print breaches
        if breaches is not None:
            breachList = oxford_comma_join(breaches)               
            speech = "Listen up " + name.split(" ", 1)[0] + ". Your email showed up in "+str(len(breaches))+" breaches: "+ breachList + ". You should rotate your passwords, start using a password manager, and enable two factor authentication on all of your accounts."
            card_title = "You've been pwned "+ name.split(" ", 1)[0]
            card_text = "Your email showed up in "+str(len(breaches))+" breaches: "+ breachList + ".\nYou should rotate your passwords, start using a password manager, and enable two factor authentication on all of your accounts."
            return statement(speech).simple_card(title=card_title, content=card_text)

        else:
            speech = "Good news "+ name.split(" ", 1)[0] + "! Your email address " + email + " didn't appear in any breaches. But remain vigilant, because the recent Equifax breah is enormous. You might want to consider implenting credit freezes at all three credit bureaus."
            card_title = "Good news "+ name.split(" ", 1)[0]+ "!"
            card_text = "Your email address " + email + " didn't appear in any breaches.\nBut remain vigilant, the recent Equifax breah is enormous. You might want to consider implenting credit freezes at all three credit bureaus." 
            return statement(speech).simple_card(title=card_title, content=card_text)

if __name__ == "__main__":
	app.run(debug=os.environ['DEBUG'])
