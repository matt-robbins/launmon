
function setButtonSubscribed(button, subscribed) {
    if(subscribed) {
        button.removeClass("btn-outline-primary").addClass("btn-primary")
    }
    else {
        button.removeClass("btn-primary").addClass("btn-outline-primary")
    }
}

function isButtonSubscribed(button) {
    return button.hasClass("btn-primary")
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
                    window.subscriptions = list
                    setButtonSubscribed($("#subscribe-"+item), list.includes(item))
                })
            })
        })
        }
    });
}

function unsubscribeFrom(location) {
    url = "/unsubscribe?location="+location+"&url="+encodeURIComponent(window.subscriptionEndpoint)
    fetch(url).then((resp) => {
        setButtonSubscribed($("subscribe-"+location), false)
    })
    return
}