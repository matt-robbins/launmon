from flask import Flask, render_template, request, jsonify, make_response, send_from_directory
import getstatus
import db
import json
from datetime import datetime

app = Flask(__name__)
db = db.LaundryDb()

STATUS = ["none", "wash", "dry", "both"]

@app.route('/webpush-sw.js')
def sw():
    response=make_response(
        send_from_directory('static','webpush-sw.js'))
    #change the content header file. Can also omit; flask will handle correctly.
    response.headers['Content-Type'] = 'application/javascript'
    return response

@app.route("/")
def hello():
    names = db.getNames()
    names.reverse()
    return render_template(
        "laundry.html",
        names=names,
        weekday=int(datetime.today().strftime("%w")),
    )

@app.route('/favicon.ico')
def favicon():
    response=make_response(send_from_directory('static','favicon.ico'))

    response.headers['Content-Type'] = 'image/vnd.microsoft.icon'
    return response

@app.route("/icons/<path:path>")
def getIcon(path):
    return send_from_directory('static/icons',path)

@app.route("/subscription",methods = ['POST'])
def subscribe():
    if request.method == 'POST':
        data = request.get_json()

        ep = data['subscription']['endpoint']
        sub = json.dumps(data['subscription'])
        loc = data['machine']

        db.insertSubscription(ep,loc,sub)
        return "!"
    return "?"

@app.route("/check-subscription")
def check_subscription(endpoint=""):
    endpoint = request.args.get("url", "", type=str)
    sub = db.checkSubscription(endpoint)
    return jsonify(sub)

@app.route("/unsubscribe")
def unsubscribe():
    endpoint = request.args.get("url","", type=str)
    location = request.args.get("location","", type=str)
    db.deleteSubscription(endpoint,location)
    return "{}"

@app.route("/status")
def status():
    return "???"


@app.route("/status-json")
def status_json():
    statusd = db.getLatest()

    d = dict(zip([s[0] for s in statusd], [s[1:] for s in statusd]))

    return jsonify(d)


@app.route("/v2/status-json")
def status_json_v2():
    status = [
        {
            "floor": line[0],
            "wash": line[1] in ("wash", "both"),
            "dry": line[1] in ("dry", "both"),
            "time": line[2],
            "last_seen": line[3],
            "location": line[4],
        }
        for line in db.getLatest()
    ]

    return jsonify(status)


@app.route("/histogram")
def histogram():
    location = request.args.get("location", "4", type=str)
    weekday = request.args.get("weekday", "0", type=str)
    tzoff = request.args.get("tzoff", 0, type=int)
    hist = db.getHist(location, weekday, tzoff)
    return render_template("hist.html", hist=hist, location=location, day=weekday)


@app.route("/histogram-json")
def histogram_json():
    location = request.args.get("location", "4", type=str)
    weekday = request.args.get("weekday", "0", type=str)
    tzoff = request.args.get("tzoff", "0", type=int)
    hist = db.getHist(location, weekday, tzoff)
    return jsonify(hist)


@app.route("/event-json")
def events_json():
    location = request.args.get("location", "all", type=str)
    hours = request.args.get("hours", 24, type=int)
    ev = db.getEvents(location, hours)
    dict = {"time": [e[0] for e in ev], "status": [e[1] for e in ev]}
    return jsonify(dict)


@app.route("/cycles-json")
def cycles_json():
    location = request.args.get("location", "all", type=str)
    hours = request.args.get("hours", 24, type=int)
    type = request.args.get("type", "dry", type=str)
    if type == "wash":
        ev = db.getWashCycles(location, hours)
    else:
        ev = db.getDryCycles(location, hours)

    events = []
    for e in ev:
        events.append({"start": e[0],"end": e[1]})

    return jsonify(events)


@app.route("/rawcurrent-json")
def current_json():
    location = request.args.get("location", "3", type=str)
    minutes = request.args.get("minutes", -60, type=int)
    res = db.getCurrent(location, minutes)

    dict = {"time": [c[2] for c in res], "current": [c[1] for c in res]}
    return jsonify(dict)


@app.route("/rawcurrent-range-json")
def current_range_json():
    location = request.args.get("location", "3", type=str)
    start = request.args.get("start", "", type=str)
    end = request.args.get("end", "", type=str)
    res = db.getCurrentRange(location, start, end)

    dict = {"time": [c[2] for c in res], "current": [c[1] for c in res]}
    return jsonify(dict)


@app.route("/current-graph")
def current_graph():
    return None


@app.route("/wash")
def washing():
    s = getstatus.getstatus()

    if s in [0, 2]:
        return "1"
    else:
        return "0"


if __name__ == "__main__":
    app.run(host="0.0.0.0")
