from flask import Flask, render_template, request
import getstatus
import constants as const
import json
import db
from datetime import datetime

app = Flask(__name__)
db = db.LaundryDb()

STATUS = ["none","wash","dry","both"]
@app.route("/")
def hello():
    return render_template('laundry.html', 
        names = ['Fourth Floor','Third Floor', 'Second Floor', 'Basement'], 
        weekday = int(datetime.today().strftime('%w')))

@app.route("/status")
def status():
    return "???"

@app.route("/status-json")
def status_json():
    status = {'1':'???','2':'???','3':'???','4':'???'}
    statusd = db.getLatest()

    d = dict(zip([s[0] for s in statusd],[s[1:] for s in statusd]))

    return json.dumps(d)

    # for floor in ['1','2','3','4']:
    #     try:
    #         with open(const.STATUS_PATH+'/'+floor,'r') as f:
    #             status[floor] = f.read()
    #     except Exception as e:
    #         status[floor] = 'unknown'

    # return json.dumps(status)

@app.route("/histogram")
def histogram(location="4",weekday=0):
    location = request.args.get('location', "4", type=str)
    weekday = request.args.get('weekday', "0", type=str)
    hist = db.getHist(location,weekday)
    return render_template('hist.html', hist = hist, location = location, day = weekday)

@app.route("/histogram-json")
def histogram_json():
    location = request.args.get('location', "4", type=str)
    weekday = request.args.get('location', "0", type=str)
    hist = db.getHist(location,weekday)
    return json.dumps(hist)

@app.route("/event-json")
def events_json():
    location = request.args.get('location', "all", type=str)
    hours = request.args.get('hours',24, type=int)
    ev = db.getEvents(location,hours)
    return json.dumps(ev)

@app.route("/wash")
def washing():
    s = getstatus.getstatus()

    if (s in [0,2]):
        return "1"
    else:
        return "0" 

if __name__ == "__main__":
    app.run(host='0.0.0.0')
