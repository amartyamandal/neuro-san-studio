// Fix for Windows/WSL environments - auto-injected by fix_connections.sh
(function() {
    console.log('Applying connection fixes for Windows/WSL environments');
    
    // Replace any uses of localhost with localhost
    var originalFetch = window.fetch;
    window.fetch = function(url, options) {
        if (typeof url === 'string' && url.includes('localhost')) {
            url = url.replace('localhost', 'localhost');
            console.log('Redirecting fetch from localhost to localhost:', url);
        }
        return originalFetch.call(this, url, options);
    };
    
    // Replace any uses of localhost in XMLHttpRequest
    var originalOpen = XMLHttpRequest.prototype.open;
    XMLHttpRequest.prototype.open = function(method, url, async, user, password) {
        if (typeof url === 'string' && url.includes('localhost')) {
            url = url.replace('localhost', 'localhost');
            console.log('Redirecting XHR from localhost to localhost:', url);
        }
        return originalOpen.call(this, method, url, async, user, password);
    };
    
    // Fix WebSocket connections
    var originalWebSocket = window.WebSocket;
    window.WebSocket = function(url, protocols) {
        if (typeof url === 'string' && url.includes('localhost')) {
            url = url.replace(/0\.0\.0\.0/g, 'localhost');
            console.log('Redirecting WebSocket from localhost to localhost:', url);
        }
        return new originalWebSocket(url, protocols);
    };
    
    // Fix EventSource connections (for SSE)
    var originalEventSource = window.EventSource;
    if (originalEventSource) {
        window.EventSource = function(url, options) {
            if (typeof url === 'string' && url.includes('localhost')) {
                url = url.replace(/0\.0\.0\.0/g, 'localhost');
                console.log('Redirecting EventSource from localhost to localhost:', url);
            }
            return new originalEventSource(url, options);
        };
    }
    
    console.log('Enhanced connection fixes applied successfully');
})();
