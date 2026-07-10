"""
Local usage data server for Claude token widget.
Run: python usage_server.py
Serves on http://localhost:3999
"""
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
import json, time, os
from urllib.parse import urlparse

DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'usage_data.json')
FLAG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'refresh_flag.txt')

def load_data():
    try:
        with open(DATA_FILE) as f:
            return json.load(f)
    except:
        return {"sessionPct": 0, "weeklyPct": 0, "hoursLeft": 0, "minsLeft": 0, "weeklyReset": "Sun 2:00 PM", "updatedAt": 0}

def save_data(d):
    try:
        with open(DATA_FILE, 'w') as f:
            json.dump(d, f)
    except:
        pass

data = load_data()

HTML = """<!DOCTYPE html><html><head><meta charset="utf-8"><title>Claude Usage</title>
<style>
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
:root{--bg:#0B111A;--surface:#121C28;--surface2:#172234;--border:#1A2A3C;--border2:#243549;--text:#BDD0E4;--muted:#4A6882;--muted2:#2E4459;--accent:#17CFAF;--warn:#E8A030;--crit:#E04848}
body{background:var(--bg);color:var(--text);font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',system-ui,sans-serif;min-height:100vh;display:grid;place-items:center;padding:24px 16px}
.container{width:100%;max-width:440px;display:flex;flex-direction:column;gap:12px}
.header{display:flex;align-items:center;justify-content:space-between;padding:0 2px 4px}
.header-title{font-size:11px;font-weight:600;letter-spacing:.12em;text-transform:uppercase;color:var(--muted)}
.header-right{display:flex;align-items:center;gap:10px}
.status-pill{display:flex;align-items:center;gap:5px;font-size:10.5px;color:var(--muted);letter-spacing:.04em}
.live-dot{width:6px;height:6px;border-radius:50%;background:var(--accent);animation:pulse 2s ease-in-out infinite}
.live-dot.error{background:var(--crit);animation:none}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.3}}
.refresh-btn{background:none;border:none;color:var(--muted);cursor:pointer;padding:2px;display:flex;align-items:center;transition:color .15s;font-family:inherit}
.refresh-btn:hover{color:var(--text)}
.refresh-btn.spinning svg{animation:spin .8s linear infinite}
@keyframes spin{to{transform:rotate(360deg)}}
.card{background:var(--surface);border:1px solid var(--border);border-radius:12px;padding:20px 22px;position:relative;overflow:hidden}
.card::before{content:'';position:absolute;top:0;left:0;right:0;height:1px;background:linear-gradient(90deg,transparent,var(--border2),transparent)}
.card-label{font-size:10.5px;font-weight:600;letter-spacing:.1em;text-transform:uppercase;color:var(--muted);margin-bottom:16px}
.session-body{display:flex;align-items:center;gap:20px}
.ring-wrap{flex-shrink:0;position:relative;width:96px;height:96px}
.ring-wrap canvas{display:block}
.ring-center{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:1px}
.ring-pct{font-family:ui-monospace,'SF Mono','Fira Code',monospace;font-size:22px;font-weight:700;font-variant-numeric:tabular-nums;line-height:1;color:var(--text)}
.ring-sub{font-size:9.5px;letter-spacing:.08em;text-transform:uppercase;color:var(--muted)}
.session-meta{flex:1;display:flex;flex-direction:column;gap:10px}
.timer-block{display:flex;flex-direction:column;gap:3px}
.timer-label{font-size:10px;letter-spacing:.08em;text-transform:uppercase;color:var(--muted)}
.timer-value{font-family:ui-monospace,'SF Mono','Fira Code',monospace;font-size:28px;font-weight:600;font-variant-numeric:tabular-nums;letter-spacing:.02em;line-height:1;color:var(--text);transition:color .3s}
.timer-value.warn{color:var(--warn)}.timer-value.crit{color:var(--crit)}
.reset-note{font-size:11px;color:var(--muted)}
.weekly-body{display:flex;flex-direction:column;gap:14px}
.weekly-top{display:flex;align-items:flex-end;justify-content:space-between}
.weekly-pct{font-family:ui-monospace,'SF Mono','Fira Code',monospace;font-size:36px;font-weight:700;font-variant-numeric:tabular-nums;line-height:1;color:var(--text)}
.weekly-reset{font-size:11.5px;color:var(--muted);padding-bottom:4px;text-align:right;line-height:1.5}
.weekly-reset strong{color:var(--text);font-weight:600}
.bar-track{width:100%;height:6px;background:var(--muted2);border-radius:99px;overflow:hidden}
.bar-fill{height:100%;border-radius:99px;transition:width .8s cubic-bezier(.4,0,.2,1),background .4s}
.bar-fill.good{background:linear-gradient(90deg,#0FA88E,var(--accent))}
.bar-fill.warn{background:linear-gradient(90deg,#C07820,var(--warn))}
.bar-fill.crit{background:linear-gradient(90deg,#B82828,var(--crit))}
.next-update{text-align:center;font-size:10.5px;color:var(--muted);padding:2px 0}
</style></head><body>
<div class="container">
  <div class="header">
    <span class="header-title">Claude Usage</span>
    <div class="header-right">
      <span class="status-pill"><span class="live-dot" id="liveDot"></span><span id="statusText">connecting…</span></span>
      <button class="refresh-btn" id="refreshBtn" onclick="triggerRefresh()" title="Refresh now">
        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
          <polyline points="23 4 23 10 17 10"/><polyline points="1 20 1 14 7 14"/>
          <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/>
        </svg>
      </button>
    </div>
  </div>
  <div class="card">
    <div class="card-label">Current Session · 5-hour window</div>
    <div class="session-body">
      <div class="ring-wrap">
        <canvas id="ringCanvas" width="96" height="96"></canvas>
        <div class="ring-center"><span class="ring-pct" id="sessionPct">—</span><span class="ring-sub">used</span></div>
      </div>
      <div class="session-meta">
        <div class="timer-block"><span class="timer-label">Resets in</span><span class="timer-value" id="sessionTimer">—:——:——</span></div>
        <div class="reset-note">Resets at <strong id="sessionResetTime">—</strong></div>
      </div>
    </div>
  </div>
  <div class="card">
    <div class="card-label">Weekly · All models</div>
    <div class="weekly-body">
      <div class="weekly-top">
        <span class="weekly-pct" id="weeklyPct">—</span>
        <div class="weekly-reset" id="weeklyResetLabel">—</div>
      </div>
      <div class="bar-track"><div class="bar-fill good" id="weeklyBar" style="width:0%"></div></div>
    </div>
  </div>
  <div class="next-update" id="nextUpdate">Next update in —</div>
</div>
<script>
const POLL=10*60;
let st={sessionPct:0,weeklyPct:0,secondsLeft:0,weeklyReset:'',ok:false};
let nxt=POLL,iv=null;
function drawRing(p){
  const c=document.getElementById('ringCanvas'),ctx=c.getContext('2d'),dpr=window.devicePixelRatio||1,sz=96;
  c.width=sz*dpr;c.height=sz*dpr;c.style.width=sz+'px';c.style.height=sz+'px';ctx.scale(dpr,dpr);
  const cx=sz/2,cy=sz/2,r=36,s=-Math.PI/2;
  ctx.beginPath();ctx.arc(cx,cy,r,0,Math.PI*2);ctx.strokeStyle='rgba(46,68,89,.8)';ctx.lineWidth=7;ctx.stroke();
  if(p>0){
    const g=ctx.createLinearGradient(cx-r,cy,cx+r,cy);
    if(p>=90){g.addColorStop(0,'#B82828');g.addColorStop(1,'#E04848')}
    else if(p>=70){g.addColorStop(0,'#C07820');g.addColorStop(1,'#E8A030')}
    else{g.addColorStop(0,'#0FA88E');g.addColorStop(1,'#17CFAF')}
    ctx.beginPath();ctx.arc(cx,cy,r,s,s+(p/100)*Math.PI*2);ctx.strokeStyle=g;ctx.lineWidth=7;ctx.lineCap='round';ctx.stroke();
  }
}
function pad(n){return String(n).padStart(2,'0')}
function fmt(s){if(s<=0)return'0:00:00';return`${Math.floor(s/3600)}:${pad(Math.floor(s%3600/60))}:${pad(s%60)}`}
function absTime(s){const d=new Date(Date.now()+s*1000),h=d.getHours(),m=d.getMinutes();return`${h%12||12}:${pad(m)} ${h>=12?'PM':'AM'}`}
function cls(p){return p>=90?'crit':p>=70?'warn':'good'}
function render(){
  drawRing(st.sessionPct);
  document.getElementById('sessionPct').textContent=st.sessionPct>0?st.sessionPct+'%':'—';
  const t=document.getElementById('sessionTimer');
  t.className='timer-value '+(st.secondsLeft<600?'crit':st.secondsLeft<1800?'warn':'');
  t.textContent=st.secondsLeft>0?fmt(st.secondsLeft):'—:——:——';
  document.getElementById('sessionResetTime').textContent=st.secondsLeft>0?absTime(st.secondsLeft):'—';
  document.getElementById('weeklyPct').textContent=st.weeklyPct>0?st.weeklyPct+'%':'—';
  const bar=document.getElementById('weeklyBar');bar.style.width=st.weeklyPct+'%';bar.className='bar-fill '+cls(st.weeklyPct);
  document.getElementById('weeklyResetLabel').innerHTML=st.weeklyReset?`Resets <strong>${st.weeklyReset}</strong>`:'—';
  document.getElementById('liveDot').className='live-dot'+(st.ok?'':' error');
  document.getElementById('statusText').textContent=st.ok?'live':'no data';
  const mn=Math.floor(nxt/60),sc=nxt%60;
  document.getElementById('nextUpdate').textContent=`Next update in ${mn>0?mn+'m ':''}${pad(sc)}s`;
}
async function fetchNow(){
  document.getElementById('refreshBtn').classList.add('spinning');
  try{
    const r=await fetch('/data',{cache:'no-store'});
    if(!r.ok)throw 0;
    const d=await r.json();
    st.ok=true;st.sessionPct=d.sessionPct||0;st.weeklyPct=d.weeklyPct||0;
    st.secondsLeft=(d.hoursLeft||0)*3600+(d.minsLeft||0)*60;
    st.weeklyReset=d.weeklyReset||'';nxt=POLL;
  }catch(e){st.ok=false}
  document.getElementById('refreshBtn').classList.remove('spinning');
  render();
}
async function triggerRefresh(){
  const btn=document.getElementById('refreshBtn');
  btn.classList.add('spinning');
  document.getElementById('statusText').textContent='refreshing…';
  // Snapshot current updatedAt before triggering
  let prevUpdatedAt=0;
  try{const r=await fetch('/data',{cache:'no-store'});const d=await r.json();prevUpdatedAt=d.updatedAt||0;}catch(e){}
  try{ await fetch('/trigger',{method:'GET',cache:'no-store'}); }catch(e){}
  // Poll /data every 2s for up to 30s waiting for updatedAt to change
  const ts=Date.now();
  const poll=setInterval(async()=>{
    try{
      const r=await fetch('/data',{cache:'no-store'});
      const d=await r.json();
      if(d.updatedAt&&d.updatedAt!==prevUpdatedAt){
        clearInterval(poll);
        st.ok=true;st.sessionPct=d.sessionPct||0;st.weeklyPct=d.weeklyPct||0;
        st.secondsLeft=(d.hoursLeft||0)*3600+(d.minsLeft||0)*60;
        st.weeklyReset=d.weeklyReset||'';nxt=POLL;
        btn.classList.remove('spinning');
        render();
        return;
      }
      // Stop spinning after 15s even without update — show whatever is on server
      if(Date.now()-ts>15000){
        clearInterval(poll);
        if(d.sessionPct){st.ok=true;st.sessionPct=d.sessionPct||0;st.weeklyPct=d.weeklyPct||0;st.secondsLeft=(d.hoursLeft||0)*3600+(d.minsLeft||0)*60;st.weeklyReset=d.weeklyReset||'';}
        btn.classList.remove('spinning');
        render();
      }
    }catch(e){
      if(Date.now()-ts>15000){clearInterval(poll);btn.classList.remove('spinning');render();}
    }
  },2000);
}
function tick(){
  if(st.secondsLeft>0)st.secondsLeft--;
  if(--nxt<=0){nxt=POLL;fetchNow();return}
  render();
}
fetchNow().then(()=>{if(iv)clearInterval(iv);iv=setInterval(tick,1000)});
</script></body></html>"""


class Handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self._cors()
        self.end_headers()

    def do_GET(self):
        path = urlparse(self.path).path  # strip query string
        if path == '/data':
            self.send_response(200)
            self._cors()
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(data).encode())
        elif path == '/trigger':
            try:
                with open(FLAG_FILE, 'w') as f:
                    f.write(str(int(time.time())))
                self.send_response(200)
                self._cors()
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(b'{"ok":true}')
            except Exception:
                self.send_response(500)
                self.end_headers()
        elif path == '/check':
            self.send_response(200)
            self._cors()
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            if os.path.exists(FLAG_FILE):
                try:
                    os.remove(FLAG_FILE)
                except Exception:
                    pass
                self.wfile.write(b'{"task":"usage"}')
            else:
                self.wfile.write(b'{"task":null}')
        elif path in ('/', '/widget'):
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(HTML.encode())
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        path = urlparse(self.path).path
        if path == '/update':
            length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(length)
            try:
                payload = json.loads(body)
                data.update(payload)
                data['updatedAt'] = int(time.time())
                save_data(data)
                self.send_response(200)
                self._cors()
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(b'{"ok":true}')
                print(f"Updated: session={data['sessionPct']}% weekly={data['weeklyPct']}% resets_in={data['hoursLeft']}h{data['minsLeft']}m")
            except Exception as e:
                self.send_response(400)
                self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()

    def _cors(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')

    def log_message(self, fmt, *args):
        pass

if __name__ == '__main__':
    server = ThreadingHTTPServer(('localhost', 3999), Handler)
    print(f"Usage server running at http://localhost:3999 (data: {DATA_FILE})")
    server.serve_forever()
