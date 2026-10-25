// Listen to every tab update in Chrome
chrome.tabs.onUpdated.addListener(async (tabId, changeInfo, tab) => {
    // Only trigger when a new URL starts loading (ignore local chrome:// pages)
    if (changeInfo.status === 'loading' && tab.url && tab.url.startsWith('http')) {
      console.log("[TrustLens] Scanning:", tab.url);
  
      try {
        // Shoot the URL to your live FastAPI backend
        const response = await fetch("http://127.0.0.1:8000/api/v1/scan", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ url: tab.url })
        });
  
        const data = await response.json();
        console.log("[TrustLens] AI Verdict:", data.overall_risk_score);
  
        // If the AI is highly confident it's malicious, nuke the page
        if (data.overall_risk_score >= 75) {
          chrome.scripting.executeScript({
            target: { tabId: tabId },
            func: injectLockdownScreen,
            args: [data]
          });
        }
      } catch (err) {
        console.error("[TrustLens] Core offline or unreachable.", err);
      }
    }
  });
  
  // This function gets injected directly into the malicious webpage to overwrite it
  function injectLockdownScreen(scanData) {
    // Overwrite the entire HTML of the dangerous site
    document.documentElement.innerHTML = `
      <head><title>Threat Blocked | TrustLens AI</title></head>
      <body style="margin:0; padding:0; background-color:#0B0F19; color:white; font-family:system-ui, sans-serif; display:flex; flex-direction:column; justify-content:center; align-items:center; height:100vh; overflow:hidden;">
        <div style="background-color:#161F30; border: 1px solid #ef4444; border-radius: 12px; padding: 40px; max-width: 600px; text-align:center; box-shadow: 0 0 50px rgba(239, 68, 68, 0.2);">
          <h1 style="color:#ef4444; font-size: 2.5rem; margin-top:0; margin-bottom: 10px;">⚠️ CONNECTION SEVERED</h1>
          <h2 style="color:#f87171; font-weight: normal; margin-bottom: 30px;">TrustLens AI Interceptor blocked a severe threat.</h2>
          
          <div style="background-color:#0B0F19; padding: 20px; border-radius: 8px; border: 1px solid #334155; text-align:left; margin-bottom: 30px;">
              <p style="margin: 0 0 10px 0; color: #94a3b8; font-family: monospace;">TARGET_URL: <span style="color:white;">${scanData.target_url}</span></p>
              <p style="margin: 0 0 10px 0; color: #94a3b8; font-family: monospace;">AI_CONFIDENCE: <span style="color:#ef4444; font-weight:bold;">${scanData.overall_risk_score}/100</span></p>
              <p style="margin: 0; color: #94a3b8; font-family: monospace;">TELEMETRY: <span style="color:white;">Length=${scanData.metrics.url_length}, Entropy=${scanData.metrics.domain_entropy}</span></p>
          </div>
  
          <p style="color:#94a3b8; margin-bottom: 30px; font-size: 0.9rem;">${scanData.explanation}</p>
          
          <button onclick="window.history.back()" style="padding: 12px 24px; background-color: #059669; color: white; border: none; border-radius: 6px; font-size: 1rem; cursor: pointer; font-weight: bold; transition: background 0.2s;">
            RETURN TO SAFETY
          </button>
        </div>
      </body>
    `;
  }