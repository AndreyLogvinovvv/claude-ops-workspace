if (!window.__claudeUsagePolling) {
  window.__claudeUsagePolling = true;

  // Your Claude organization id. Find it in the browser Network tab on claude.ai:
  // look for a request to /api/organizations/<ORG_ID>/... and copy the id.
  const ORG = 'YOUR_ORG_ID';

  setInterval(async () => {
    try {
      const r = await fetch('http://localhost:3999/check', { cache: 'no-store' });
      const d = await r.json();
      if (d.task !== 'usage') return;

      const u = await fetch(`/api/organizations/${ORG}/usage`);
      const j = await u.json();
      const fh = j.five_hour, sd = j.seven_day;
      const sessionPct = fh?.utilization || 0;
      const weeklyPct = sd?.utilization || 0;
      const diff = new Date(fh?.resets_at) - Date.now();
      const hoursLeft = Math.max(0, Math.floor(diff / 3600000));
      const minsLeft = Math.max(0, Math.floor((diff % 3600000) / 60000));
      const wr = new Date(sd?.resets_at);
      const weeklyReset = wr.toLocaleDateString('en', { weekday: 'short' }) + ' ' +
        wr.toLocaleTimeString('en', { hour: 'numeric', minute: '2-digit' });

      await fetch('http://localhost:3999/update', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ sessionPct, weeklyPct, hoursLeft, minsLeft, weeklyReset })
      });
    } catch (e) {}
  }, 2000);
}
