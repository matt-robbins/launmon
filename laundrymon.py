from flask import Flask, render_template
import getstatus
import constants as const
import json
import db

app = Flask(__name__)
db = db.LaundryDb()

STATUS = ["none","wash","dry","both"]
@app.route("/")
def hello():
    return render_template('laundry.html')

@app.route("/status")
def status():
    return "???"

@app.route("/status-json")
def status_json():
    status = {'1':'???','2':'???','3':'???','4':'???'}
    statusd = db.getLatest()
    d = dict(zip([s[0] for s in statusd],[s[1] for s in statusd]))

    return json.dumps(d)

    for floor in ['1','2','3','4']:
        try:
            with open(const.STATUS_PATH+'/'+floor,'r') as f:
                status[floor] = f.read()
        except Exception as e:
            status[floor] = 'unknown'

    return json.dumps(status)

@app.route("/wash")
def washing():
    s = getstatus.getstatus()

    if (s in [0,2]):
        return "1"
    else:
        return "0" 

if __name__ == "__main__":
    app.run(host='0.0.0.0')
