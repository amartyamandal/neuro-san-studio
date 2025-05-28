/**
 * socketio_direct_fix.js - Direct fixes for Socket.IO connections to 0.0.0.0
 * 
 * This script directly intercepts Socket.IO before it's initialized and applies
 * critical fixes specifically to handle the 0.0.0.0 to localhost conversion issue.
 * 
 * IMPORTANT: This script must be loaded BEFORE socket.io.js
 */

// This script must run before Socket.IO is loaded
console.log('🔧 Setting up Socket.IO direct fix');

(function() {
    // Store original properties we need to modify
    var originalDescriptors = {};
    
    // Save the original document.domain descriptor
    try {
        originalDescriptors.domain = Object.getOwnPropertyDescriptor(document, 'domain');
    } catch (e) {
        console.error('Failed to get document.domain descriptor:', e);
    }
    
    // Override document.domain with a getter/setter that always changes 0.0.0.0 to localhost
    try {
        Object.defineProperty(document, 'domain', {
            get: function() {
                var domain = originalDescriptors.domain.get.call(document);
                return domain === '0.0.0.0' ? 'localhost' : domain;
            },
            set: function(value) {
                if (value === '0.0.0.0') {
                    console.log('⚠️ Intercepted attempt to set document.domain to 0.0.0.0, using localhost instead');
                    originalDescriptors.domain.set.call(document, 'localhost');
                } else {
                    originalDescriptors.domain.set.call(document, value);
                }
            },
            configurable: true
        });
        console.log('✅ Successfully patched document.domain');
    } catch (e) {
        console.error('❌ Failed to patch document.domain:', e);
    }
    
    // Helper to check if a URL uses 0.0.0.0
    function checkAndFixUrl(url) {
        if (typeof url === 'string' && url.includes('0.0.0.0')) {
            return url.replace(/0\.0\.0\.0/g, 'localhost');
        }
        return url;
    }
    
    // Create a wrapper for socket.io that intercepts all connection attempts
    window.socketioDirectFix = {
        // Store connection attempts to detect patterns
        connectionAttempts: [],
        
        // Record a connection attempt
        recordAttempt: function(url, options) {
            this.connectionAttempts.push({
                timestamp: Date.now(),
                originalUrl: url,
                fixedUrl: checkAndFixUrl(url),
                options: options
            });
            
            // If we've collected multiple attempts, analyze them
            if (this.connectionAttempts.length >= 3) {
                this.analyzeConnectionPatterns();
            }
        },
        
        // Analyze connection patterns to detect issues
        analyzeConnectionPatterns: function() {
            var patterns = this.connectionAttempts;
            var failedUrls = patterns.filter(p => p.originalUrl && p.originalUrl.includes && p.originalUrl.includes('0.0.0.0'));
            
            if (failedUrls.length > 0) {
                console.warn('⚠️ Detected multiple connection attempts to 0.0.0.0 addresses');
                console.log('Connection patterns:', patterns);
                
                // Add diagnostic info to the page if the help element exists
                var diagEl = document.getElementById('connection-diagnostics');
                if (diagEl) {
                    var html = '<br><strong>Connection diagnosis:</strong><br>';
                    html += 'Detected ' + failedUrls.length + ' attempts to connect to 0.0.0.0 addresses.<br>';
                    html += 'This is a known issue in Windows/WSL environments.';
                    diagEl.innerHTML += html;
                }
            }
        }
    };
    
    // Wait for socket.io to be loaded, then patch it
    var checkSocketIO = setInterval(function() {
        if (window.io) {
            clearInterval(checkSocketIO);
            
            // Save the original connect method
            var originalSocketIO = window.io;
            
            // Override with our version that forces localhost
            window.io = function() {
                var url = arguments[0];
                var options = arguments[1] || {};
                
                // Record this connection attempt
                window.socketioDirectFix.recordAttempt(url, options);
                
                // Always convert 0.0.0.0 to localhost
                if (typeof url === 'string' && url.includes('0.0.0.0')) {
                    arguments[0] = url.replace(/0\.0\.0\.0/g, 'localhost');
                    console.log('� Socket.IO redirecting from', url, 'to', arguments[0]);
                }
                
                // Always ensure reconnection is enabled
                if (!options.reconnection) {
                    options.reconnection = true;
                    options.reconnectionAttempts = options.reconnectionAttempts || 10;
                    arguments[1] = options;
                }
                
                return originalSocketIO.apply(this, arguments);
            };
            
            // Copy over any properties from the original
            for (var prop in originalSocketIO) {
                if (originalSocketIO.hasOwnProperty(prop)) {
                    window.io[prop] = originalSocketIO[prop];
                }
            }
            
            console.log('✅ Socket.IO direct fix successfully applied');
        }
    }, 10);
})();
