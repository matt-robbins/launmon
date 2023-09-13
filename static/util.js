
function setButtonSubscribed(button, subscribed) {
    if(subscribed) {
        button.removeClass("btn-outline-primary").addClass("btn-primary")
    }
    else {
        button.removeClass("btn-primary").addClass("btn-outline-primary")
    }
}

function updateSubscriptions() {
    
    navigator.serviceWorker.getRegistration("/").then((registration) => {
        if (registration) {
        registration.pushManager.getSubscription().then((subscription) => {
            url = "/check-subscription?url="+encodeURIComponent(subscription.endpoint)
            fetch(url)
            .then((resp) => resp.json())
            .then((list) => { 
                ["1","2","3","4"].forEach(item => {
                    setButtonSubscribed($("#subscribe-"+item), list.includes(item))
                })
            })
        })
        console.log("registered!")
        }
    });
}