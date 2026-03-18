import asyncio
import websockets
import json
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

phone = None
pc = None

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")
    def log_message(self, format, *args):
        pass

def run_http(port):
    server = HTTPServer(("0.0.0.0", port), HealthHandler)
    server.serve_forever()

async def handler(websocket):
    global phone, pc
    try:
        msg = await websocket.recv()
        data = json.loads(msg)

        if data["client"] == "phone":
            phone = websocket
            print("✅ Telefon ulandi")
            await websocket.send(json.dumps({"status": "ok"}))
        elif data["client"] == "pc":
            pc = websocket
            print("✅ PC ulandi")
            await websocket.send(json.dumps({"status": "ok"}))

        async for message in websocket:
            if websocket == pc and phone:
                await phone.send(message)
                print(f"PC→Tel: {message}")
            elif websocket == phone and pc:
                await pc.send(message)
                print(f"Tel→PC: {message}")
    except Exception as e:
        print(f"Xato: {e}")
    finally:
        if websocket == phone: phone = None
        if websocket == pc: pc = None

async def main():
    http_port = int(os.environ.get("PORT", 10000))
    ws_port = 8765

    t = threading.Thread(target=run_http, args=(http_port,), daemon=True)
    t.start()

    print(f"🚀 HTTP: {http_port}, WS: {ws_port}")
    async with websockets.serve(handler, "0.0.0.0", ws_port):
        await asyncio.Future()

asyncio.run(main())
