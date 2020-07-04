from flask import Flask, flash, render_template, redirect, request,\
    session, url_for, Response  
from twilio.twiml.voice_response import VoiceResponse

from ivr_survey import app

def twiml(resp):
    resp = flask.Response(str(resp))
    resp.headers['Content-Type'] = 'text/xml'
    return resp

@app.route('/')
@app.route('/survey')
def index():
    return "Hello, World!"

@app.route('/survey/description', methods=['GET','POST'])
def description():
    response = VoiceResponse()
    with response.gather(num_digits=1, action=url_for('question_one'), method='POST') as g:
        g.say(message="Thank you for calling. Please any number to get started" , loop=2)
    return twiml(response)

@app.route('survey/question_one', methods=['POST'])
def question_one():
    selected_option = request.form['Digits']


    if selected_option in option_actions.keys():
        response = VoiceResponse()
        option_actions[selected_option](response)
        return twiml(response)

    return twiml(response)