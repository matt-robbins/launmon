from flask import Flask, render_template
import getstatus

app = Flask(__name__)

STATUS = ["none","wash","dry","both"]
@app.route("/")
def hello():
    statusn=getstatus.getstatus()+1
    status = STATUS[statusn]
    print(status)
    AVAILABLE="available"
    INUSE="in use"
    AVAILABLECOL="green"
    INUSECOL="red"

    washertext = AVAILABLE
    dryertext = AVAILABLE
    washercol = AVAILABLECOL
    dryercol = AVAILABLECOL
    if (status == 'both'):
        washertext=INUSE;dryertext=INUSE;washercol=INUSECOL;dryercol=INUSECOL
    elif (status == 'wash'):
        washertext=INUSE;washercol=INUSECOL
    elif (status == "dry"):
        dryertext=INUSE;dryercol=INUSECOL
 
    return render_template('laundry.html',wcolor=washercol,wtext=washertext,dcolor=dryercol,dtext=dryertext)

@app.route("/status")
def status():
    return "%s" % (getstatus.getstatus()+1)

@app.route("/wash")
def washing():
    s = getstatus.getstatus()

    if (s in [0,2]):
        return "1"
    else:
        return "0" 

if __name__ == "__main__":
    app.run(host='0.0.0.0')
