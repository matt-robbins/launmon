running = {}
was_running = {}

function update() {
    Object.assign(was_running,running);
    fetch(`${$SCRIPT_ROOT}/v2/status-json`)
    .then((resp) => resp.json())
    .then((status) => {
        status.forEach((floorStatus) => {
        const floor = $(`#floor-${floorStatus.floor}`);
        const lastSeen = new Date(`${floorStatus.last_seen}Z`);
        const lastUpdated = new Date(`${floorStatus.time}Z`);
        
        running[floorStatus.floor] = floorStatus.wash || floorStatus.dry

        if ((Date.now() - lastSeen > 60 * 1000 ) || (floorStatus.offline == true)) {
            floor
            .find("[data-js-attr='floor-updated-at']")
            .text(`Last seen: ${lastSeen.toLocaleDateString()}`);
            floor
            .find("svg.washer")
            .attr("class", "machine washer")
            .find(".label")
            .text("Offline");
            floor
            .find("svg.dryer")
            .attr("class", "machine dryer")
            .find(".label")
            .text("Offline");
        } 
        else {
            dry_text = wash_text = "Available"
            
            if (floorStatus.wash === true) {
                wash_text = "Running"
            }
            if (floorStatus.dry === true) {
                wash_text = "Running"
            }
            if (floorStatus.ooo === true) {
                dry_text = wash_text = "Error!"
            }
            if (floorStatus.offline === true) {
                dry_text = wash_text = "Offline"
            }
            floor
            .find("[data-js-attr='floor-updated-at']")
            .text(`Last updated: ${lastUpdated.toLocaleTimeString()}`);
            floor
            .find("svg.washer")
            .attr("class", "machine washer")
            .toggleClass("running", floorStatus.wash === true)
            .toggleClass("available", floorStatus.wash === false)
            .toggleClass("ooo", floorStatus.ooo === true)
            .find(".label")
            .text(wash_text);
            floor
            .find("svg.dryer")
            .attr("class", "machine dryer")
            .toggleClass("running", floorStatus.dry === true)
            .toggleClass("available", floorStatus.dry === false)
            .toggleClass("ooo", floorStatus.ooo === true)
            .find(".label")
            .text(dry_text);
        }
        });
    });

    updateSubscriptions()
}

$(function () {
    window.subscriptions = []

    update();
    setInterval(function () {
        update();
    }, 5000);

    ws = new WebSocket("wss://laundry.375lincoln.nyc/websocket")
    ws.addEventListener("message", (event) => {
        e = JSON.parse(event.data)
        if (e.status) {
            update();
        }
    });

    console.log(window.subscriptionEndpoint)
    // set up callbacks for subscribe buttons
    for (fl = 1; fl < 5; fl++) {
        const floor = $(`#subcheck-${fl}`);

        floor.on("click", function(event) {

            console.log(event.currentTarget.id)
            machine = event.currentTarget.id.split("-")[1]
            console.log(machine)

            window.subscribe(machine=machine,unsubscribe=window.subscriptions.includes(machine))
            
        })
    }

    updateSubscriptions()
});