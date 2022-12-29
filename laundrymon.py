from flask import Flask, render_template, request, jsonify
import getstatus
import constants as const
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
    statusd = db.getLatest()

    d = dict(zip([s[0] for s in statusd],[s[1:] for s in statusd]))

    return jsonify(d)

@app.route("/v2/status-json")
def status_json_v2():
    status = [
        {
            "floor": line[0],
            "wash": line[1] in ("wash","both"),
            "dry": line[1] in ("dry", "both"),
            "time": line[2],
            "last_seen": line[3]
        } for line in db.getLatest()
    ]

    return jsonify(status)


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
    return jsonify(hist)

@app.route("/event-json")
def events_json():
    location = request.args.get('location', "all", type=str)
    hours = request.args.get('hours',24, type=int)
    ev = db.getEvents(location,hours)
    dict = {"time": [e[0] for e in ev],"status": [e[1] for e in ev]}
    return jsonify(dict)

@app.route("/cycles-json")
def cycles_json():
    location = request.args.get('location', "all", type=str)
    hours = request.args.get('hours',24, type=int)
    type = request.args.get('type', 'dry',type=str)
    if (type == "wash"):
        ev = db.getWashCycles(location,hours)
    else:
        ev = db.getDryCycles(location,hours)
    dict = {'start':[e[0] for e in ev],"end": [e[1] for e in ev]}
    return jsonify(dict)

@app.route("/rawcurrent-json")
def current_json():
    location = request.args.get('location', "3", type=str)
    minutes = request.args.get('minutes',-60, type=int)
    print(location)
    print(minutes)
    res = db.getCurrent(location,minutes)

    dict = {"time": [c[2] for c in res],"current": [c[1] for c in res]}
    return jsonify(dict)

@app.route("/rawcurrent-range-json")
def current_range_json():
    location = request.args.get('location', "3", type=str)
    start = request.args.get('start',"", type=str)
    end = request.args.get('end',"", type=str)
    res = db.getCurrentRange(location,start,end)

    dict = {"time": [c[2] for c in res],"current": [c[1] for c in res]}
    return jsonify(dict)

@app.route("/current-graph")
def current_graph():
    return None

@app.route("/wash")
def washing():
    s = getstatus.getstatus()

    if (s in [0,2]):
        return "1"
    else:
        return "0" 

if __name__ == "__main__":
    app.run(host='0.0.0.0')
