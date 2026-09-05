from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import paho.mqtt.client as mqtt
from pathlib import Path
import json

app = FastAPI()
app.mount("/static", StaticFiles(directory=Path(__file__).parent / "static"), name="static")

CONFIG_FILE = Path(__file__).parent / "trigger_sequence.json"
LOG_FILE = Path(__file__).parent / "trigger_status.log"

MQTT_BROKER = "10.10.0.175"
MQTT_PORT = 1883
MQTT_TOPIC = "hauntedporch/control"

client = mqtt.Client(protocol=mqtt.MQTTv311)
try:
    client.connect(MQTT_BROKER, MQTT_PORT, keepalive=60)
    client.loop_start()
except Exception as e:
    print(f"UI: Could not connect to MQTT broker: {e}")


def load_sequence():
    if not CONFIG_FILE.exists():
        return []
    try:
        with open(CONFIG_FILE, "r") as fh:
            cfg = json.load(fh)
        return cfg.get("sequence", [])
    except Exception:
        return []


def tail_log(n=50):
    if not LOG_FILE.exists():
        return []
    with open(LOG_FILE, "r") as fh:
        lines = fh.readlines()
    return lines[-n:]


@app.get("/", response_class=HTMLResponse)
def index():
    seq = load_sequence()
    log_lines = tail_log(100)
    html = f"""
    <html>
      <head>
        <title>Porch Trigger UI</title>
        <style>
          body {{ font-family: Arial, sans-serif; background:#111;color:#eee;padding:1em; }}
          .seq {{ background:#222;padding:1em;border-radius:8px;margin-bottom:1em }}
          .log {{ background:#000;padding:1em;border-radius:8px;height:300px;overflow:auto }}
          button {{ margin:0.25em;padding:0.5em 1em }}
        </style>
      </head>
      <body>
        <h1>Porch Trigger UI</h1>
        <div class="seq">
          <h2>Trigger Sequence</h2>
          <ol>
    """
    for entry in seq:
        device = entry.get("device")
        delay = entry.get("delay_after")
        html += f"<li>{device} (delay after: {delay}s) <button onclick=\"trigger('{device}')\">Trigger</button></li>"
    html += """
          </ol>
        </div>
        <div class="log">
          <h2>Log Tail</h2>
          <pre id="log">"""
    for l in log_lines:
        html += l.replace('<','&lt;').replace('>','&gt;')
    html += """</pre>
        </div>
        <script>
        async function trigger(device){
          const resp = await fetch('/trigger', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({device})});
          const j = await resp.json();
          alert(j.status);
        }
        // refresh log every 5s
        setInterval(async ()=>{
          const r = await fetch('/log');
          const data = await r.json();
          document.getElementById('log').textContent = data.lines.join('');
        },5000);
        </script>
      </body>
    </html>
    """
    return HTMLResponse(content=html)


@app.post('/trigger')
async def trigger_endpoint(req: Request):
    data = await req.json()
    device = data.get('device')
    if not device:
        return JSONResponse({'status':'missing device'}, status_code=400)
    try:
        client.publish(MQTT_TOPIC, device)
        return JSONResponse({'status': f'Published {device}'})
    except Exception as e:
        return JSONResponse({'status': f'Publish failed: {e}'}, status_code=500)


@app.get('/log')
async def log_endpoint():
    lines = tail_log(200)
    return JSONResponse({'lines': lines})
