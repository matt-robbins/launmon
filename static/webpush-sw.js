self.addEventListener('install', () => {
	self.skipWaiting();
});

self.addEventListener('push', function(event) {
	console.log('Push message received.');
	let notificationTitle = 'Laundry Done!';
	const notificationOptions = {
		body: 'Come and get it.',
		data: {
			url: 'https://laundry.375lincoln.nyc',
		},
	};

	if (event.data) {
		const dataText = event.data.text();
		notificationTitle = 'Laundry Done!';
		notificationOptions.body = dataText;
	}

	event.waitUntil(
		self.registration.showNotification(
			notificationTitle,
			notificationOptions,
		),
	);
});

self.addEventListener('notificationclick', function(event) {
	console.log('Notification clicked.');
	event.notification.close();

	let clickResponsePromise = Promise.resolve();
	if (event.notification.data && event.notification.data.url) {
		clickResponsePromise = clients.openWindow(event.notification.data.url);
	}

	event.waitUntil(clickResponsePromise);
});