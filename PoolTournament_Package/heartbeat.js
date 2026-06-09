// Browser heartbeat - keeps server alive while browser is open
(function() {
    let heartbeatCount = 0;
    
    function sendHeartbeat() {
        fetch('/api/heartbeat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        })
        .then(response => {
            if (response.ok) {
                heartbeatCount++;
                console.log(`💓 Heartbeat ${heartbeatCount} sent successfully`);
            }
        })
        .catch((error) => {
            console.error('❌ Heartbeat failed:', error);
        });
    }
    
    // Send heartbeat every 5 seconds
    setInterval(sendHeartbeat, 5000);
    
    // Send initial heartbeat
    sendHeartbeat();
    
    console.log('🚀 Heartbeat system started');
})();
