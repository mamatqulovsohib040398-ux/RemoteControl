import asyncio
import websockets
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

phone = None
pc = None

# HTTP health check uchun
class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")
    def log_message(self, format, *args):
        pass

def run_http():
    server = HTTPServer(("0.0.0.0", 10000), HealthHandler)
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
            elif websocket == phone and pc:
                await pc.send(message)
    except:
        if websocket == phone: phone = None
        if websocket == pc: pc = None

async def main():
    # HTTP serverni alohida threadda ishga tushirish
    t = threading.Thread(target=run_http, daemon=True)
    t.start()
    print("🚀 Server ishga tushdi!")
    async with websockets.serve(handler, "0.0.0.0", 8765):
        await asyncio.Future()

asyncio.run(main())
