
class Timeline {
    //tape_end = 0;
    //tape_start = 0;
    scale = 0;
    head = 0;
    tape_start = 0;
    tape_end = 0;
    
    constructor(div,name,duration=3600000,tracks=1) {
        this.root = div;
        this.name = name;
        this.tracks = [];

        console.log("creating timeline with name: "+name)
        console.log("tracks="+tracks)
        div.textContent = '';
        div.classList.add("timeline-container");

        this.tape = document.createElement('div');
        this.tape.classList.add("timeline-tape");
        this.tape.id = name+"-timeline";
        div.appendChild(this.tape);

        for (var i = 0; i < tracks; i++){
            var tk = document.createElement('div');
            tk.classList.add("timeline-track");
            tk.id = name+"-track-"+i;
            this.tape.append(tk);
            this.tracks[i] = tk;
            console.log(this.tracks)
        }

        this.tape_end = new Date().getTime();
        this.tape_start = this.tape_end - duration;
        this.scale = this.tape_end - this.tape_start;
        this.head = this.tape_end;
        this.zoom_center = 1;
        this.zoom = 1;

        this.zoom_update()
        //this.pd = new PinchDetector(div);
    }

    setEventPosition(ev) {
        var start = new Date(ev.timelineEvent.start+"Z").getTime();
        var end = new Date(ev.timelineEvent.end+"Z").getTime();
        var left = (1-((this.tape_end-start)/this.scale))*100;
        var width = ((end-start)/this.scale)*100;

        if (left+width < 0) {
            ev.remove();
        }

        ev.style.left = left+'%';
        ev.style.width = width+'%';
    }

    draw(events, track, cb) {

        for (const ix in events) {
            var e = events[ix];
            var ev = document.createElement('div');
            ev.classList.add("timeline-event");

            ev.id = "timeline-"+this.name+"-"+track+"-"+ix;
            ev.timelineEvent = e

            this.setEventPosition(ev);

            ev.addEventListener('click', function(ev,e) {
                cb(ev.currentTarget.timelineEvent)
            }, e);

            this.tracks[track].appendChild(ev);
        }
    }

    update(time) {
        var diff = time - this.tape_end;
        this.tape_end = time;
        this.tape_start = time - this.scale;
        for (var track of this.tape.children) {
            for (var c of track.children) {
                this.setEventPosition(c)
            }
        }
    }

    zoom_update() {
        this.tape.style.width=this.zoom*100+"%";
        //this.tape.style.left=-(this.zoom-1)*100*this.zoom_center+"%";
    }
    set setZoom(val) {
        console.log("zoom set!");
        this.zoom = val;
        this.zoom_update();
    }
    set setHead(val) {
        this.head = val
        console.log("zoom center set@");
        this.zoom_center = (val-this.tape_start)/this.scale;
        this.zoom_update();
    }
    reset() {
        //this.tape.textContent = "";
        for (var t of this.tracks) {
            t.textContent = '';
        }
        this.scale = this.tape_end - this.tape_start;
    }
    set set_tape_start(val) {
        this.reset();
    }
    set set_tape_end(val) {
        this.reset();
    }
}