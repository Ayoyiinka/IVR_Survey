from flask import Flask, flash, render_template, redirect, request, session, url_for, Response, session
from twilio.twiml.voice_response import VoiceResponse
from ivr_survey import app
from oauth2client.service_account import ServiceAccountCredentials
from ivr_survey.sheets import sheet

import gspread
import os

def twiml(resp):
    resp = Response(str(resp))
    resp.headers['Content-Type'] = 'text/xml'
    return resp

app.secret_key = os.environ['SECRET_KEY']

@app.route('/')
@app.route('/survey')
def index():
    return "Hello, World!"

@app.route('/survey/description', methods=['POST'])
def description():
    response = VoiceResponse()
    with response.gather(num_digits=1, action=url_for('question_one'), method='POST') as g:
        g.say(message="Thank you for calling to start the survey. Please press any number to get started" , loop=2, voice="alice")
        return twiml(response)
    return twiml(response)

@app.route('/survey/question_one', methods=['POST'])
def question_one():
    response = VoiceResponse()
    with response.gather(num_digits=1, action=url_for('question_two'), method="POST") as g:
        g.say('Question one. Do you own or rent a house? Please press 1 if you own a house and 2 if you rent a house', loop=2, voice="alice")
        return twiml(response)
    return twiml(response)

@app.route('/survey/question_two', methods=['POST'])
def question_two():

    digit = request.form['Digits']

    session['answers'] = []
    
    if digit == '1':
        session['answers'].append('House Owner')
    elif digit == '2': 
        session['answers'].append('Tenant')
    else:
        session['answers'].append('None of the two options')

    response = VoiceResponse()
    with response.gather(num_digits=1, action=url_for('question_three'), method="POST") as g:
        g.say('Question two. What is your marital status? Please press 1 for married and 2 for single', loop=2, voice="alice")
        return twiml(response)
    return twiml(response)

@app.route('/survey/question_three', methods=['POST'])
def question_three():
    session_id = request.values['CallSid']
    digit = request.form['Digits']

    if digit == '1':
        session['answers'].append('Married')
    elif digit == '2': 
        session['answers'].append('Single')
    else:
        session['answers'].append('None of the two options')
    session.modified = True

    response = VoiceResponse()
    with response.gather(num_digits=2, action=url_for('end_survey'), method="POST") as g:
        g.say('Final Question. How old are you?', loop=2, voice="alice")
        return twiml(response)
    return twiml(response)

@app.route('/survey/end_survey', methods=['POST'])
def end_survey():
    session_id = request.values['CallSid']
    digit = request.form['Digits']

    session['answers'].append(digit)
    session.modified = True

    sheet.insert_row(session['answers'], 2)

    response = VoiceResponse()
    response.say('Thank you for your time, please press the # key to end the call', loop=1, voice="alice")
    return twiml(response)
