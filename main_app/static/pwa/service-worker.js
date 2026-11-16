self.addEventListener("install", event => {
    event.waitUntil(self.skipWaiting());
});

self.addEventListener("activate", event => {
    event.waitUntil(self.clients.claim());
});

self.addEventListener("fetch", event => {
    const request = event.request;
    if (request.method !== "GET" || request.mode !== "navigate") {
        return;
    }

    const requestUrl = new URL(request.url);
    if (requestUrl.origin !== self.location.origin) {
        return;
    }

    event.respondWith(
        fetch(request).catch(() => new Response(
            "<!doctype html><html lang=\"en\"><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width,initial-scale=1\"><meta name=\"theme-color\" content=\"#b40a0a\"><title>Offline | The People's Era</title><body style=\"margin:0;padding:2rem;font:16px system-ui;background:#0b1120;color:#fff\"><h1>You're offline</h1><p>Reconnect to the internet and try again.</p></body></html>",
            {
                headers: { "Content-Type": "text/html; charset=utf-8" },
                status: 503,
                statusText: "Service Unavailable"
            }
        ))
    );
});
