function ajax(url, fun, parm=null) {
    var request = new XMLHttpRequest();
    request.open('GET', url, true);
    request.onload = function() {
        if (request.status >= 200 && request.status < 400) {
            // Success!
            var data = JSON.parse(request.responseText);
            fun(data, parm)
        } else {
            // We reached our target server, but it returned an error
        }
    };
    request.send();
}

var layout = {
    title: 'Current Draw Over Time',
    xaxis: {
    autorange: true
    },

    yaxis: {
    range: [0, 2000],
    autorange: false
    },
};
plot = document.getElementById('graph');
Plotly.newPlot( plot, [{
        x: [],
        y: [] }],
        layout );

var hours = 24

function draw_history_items(data,elem,loc) {
    var history = elem
    console.log(data)
    console.log(elem)
    console.log(loc)
    var scale = hours*36000;

    var colors = {'none':'white','wash':'yellow','dry':'green','both':'red'}
    for (var i = 0; i < data.start.length-1; i++){
        var ev = document.createElement('div');
        history.append(ev);

        console.log(data.start[i])
        console.log(data.end[i])
        ds = new Date(data.start[i]+"Z").getTime()
        de = new Date(data.end[i]+"Z").getTime()
        dn = new Date().getTime()

        if (!de) {
            de = dn
        }

        console.log((dn-ds)/1000)

        ev.id = "event"+i;
        ev.classList = ['history_item']
        ev.style.position = "absolute"
        ev.style.left = 100-((dn-de)/scale)+'%';
        ev.style.width = ((de-ds)/scale)+'%';
        ev.style.height = '90%';
        ev.style.top = '0px';
        ev.setAttribute('data-start', data.start[i])
        ev.setAttribute('data-end', data.end[i])
        ev.dataset.end=data.end[i]

        console.log(data.start[i])
        console.log(data.end[i])
        ev.addEventListener('click', function(ev) {
            console.log(ev)
            //console.log(this.getAttribute('data-start'))
            ajax('/rawcurrent-range-json?location='+loc+'&start='+this.getAttribute('data-start')+'&end='+this.getAttribute('data-end'), function(data) {
                Plotly.update(plot, {'x': [data.time], 'y': [data.current]})
            })
        })
    }
}
