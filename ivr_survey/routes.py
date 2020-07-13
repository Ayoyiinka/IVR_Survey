from flask import Flask, flash, render_template, redirect, request, session, url_for, Response  
from twilio.twiml.voice_response import VoiceResponse
from ivr_survey import app
from oauth2client.service_account import ServiceAccountCredentials
from ivr_survey.sheets import sheet

import gspread


def twiml(resp):
    resp = Response(str(resp))
    resp.headers['Content-Type'] = 'text/xml'
    return resp

feedback = []

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
        g.say('Question one. How would you describe your gender? Please press 1 for male and 2 for female', loop=2, voice="alice")
        return twiml(response)
    return twiml(response)

@app.route('/survey/question_two', methods=['POST'])
def question_two():
    if request.form['Digits'] == '1':
        feedback.append('Male')
    elif request.form['Digits'] == '2': 
        feedback.append('Female')
    else:
        feedback.append('Invalid input')
    response = VoiceResponse()
    with response.gather(num_digits=1, action=url_for('question_three'), method="POST") as g:
        g.say('Question two. What is your marital status? Please press 1 for married and 2 for single', loop=2, voice="alice")
        return twiml(response)
    return twiml(response)

@app.route('/survey/question_three', methods=['POST'])
def question_three():
    if request.form['Digits'] == '1':
        feedback.append('Married')
    elif request.form['Digits'] == '2':
        feedback.append('Single')
    else:
        feedback.append('Invalid input')
    response = VoiceResponse()
    with response.gather(num_digits=2, action=url_for('end_survey'), method="POST") as g:
        g.say('Final Question. How old are you?', loop=2, voice="alice")
        return twiml(response)
    return twiml(response)

@app.route('/survey/end_survey', methods=['POST'])
def end_survey():
    feedback.append(request.form['Digits'])
    sheet.insert_row(feedback[-3:], 2)
    response = VoiceResponse()
    response.say('Thank you for your time, please press the # key to end the call', loop=1, voice="alice")
    return twiml(response)
