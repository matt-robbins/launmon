const publicVapidKey = 'BCFxaPZEymM57yWrlIPuFkMdSsQjkClmmAnVfHqKVaDtGnQ_t5uA8Yq2B0mm7GxpsNRLmqKSQIr-vdxFkSRCVQc';

// Copied from the web-push documentation
const urlBase64ToUint8Array = (base64String) => {
  const padding = '='.repeat((4 - base64String.length % 4) % 4);
  const base64 = (base64String + padding)
    .replace(/\-/g, '+')
    .replace(/_/g, '/');

  const rawData = window.atob(base64);
  const outputArray = new Uint8Array(rawData.length);

  for (let i = 0; i < rawData.length; ++i) {
    outputArray[i] = rawData.charCodeAt(i);
  }
  return outputArray;
};

function askPermission() {
    return new Promise(function (resolve, reject) {
        const permissionResult = Notification.requestPermission(function (result) {
            resolve(result);
        });

        if (permissionResult) {
            permissionResult.then(resolve, reject);
        }
    }).then(function (permissionResult) {
        if (permissionResult !== 'granted') {
        throw new Error("We weren't granted permission.");
        }
    });
}

window.subscribe = async (machine=4) => {
    console.log("subscribing?")
    if (!('serviceWorker' in navigator)) {
        console.log("no service worker :(")
        return;
    }
    console.log("waiting for service worker to be ready")
    const registration = await navigator.serviceWorker.ready;

    console.log("ready")

    navigator.serviceWorker.addEventListener("message", (message) => {
        console.log("got message! updating subscriptions")
        updateSubscriptions()
    })

    askPermission()

    // Subscribe to push notifications
    const subscription = await registration.pushManager.subscribe({
        userVisibleOnly: true,
        applicationServerKey: urlBase64ToUint8Array(publicVapidKey),
    });

    console.log(subscription)
    await fetch('/subscription', {
        method: 'POST',
        body: JSON.stringify({'subscription': subscription, 'machine': machine}),
        headers: {
            'content-type': 'application/json',
        },
    });

    updateSubscriptions()
};


// Check if service workers are supported
if ('serviceWorker' in navigator) {
    console.log("registering service worker")
    navigator.serviceWorker.register('/webpush-sw.js', {
      scope: '/',
    });
  }