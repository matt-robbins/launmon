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

        if (Date.now() - lastSeen > 60 * 1000) {
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
        } else {
            floor
            .find("[data-js-attr='floor-updated-at']")
            .text(`Last updated: ${lastUpdated.toLocaleTimeString()}`);
            floor
            .find("svg.washer")
            .toggleClass("running", floorStatus.wash === true)
            .toggleClass("available", floorStatus.wash === false)
            .find(".label")
            .text(floorStatus.wash === true ? "Running" : "Available");
            floor
            .find("svg.dryer")
            .toggleClass("running", floorStatus.dry === true)
            .toggleClass("available", floorStatus.dry === false)
            .find(".label")
            .text(floorStatus.dry === true ? "Running" : "Available");
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