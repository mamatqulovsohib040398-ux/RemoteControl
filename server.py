import asyncio
import websockets
import json

phone = None
pc = None

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
    print("🚀 Server ishga tushdi! Port: 8765")
    async with websockets.serve(handler, "0.0.0.0", 8765):
        await asyncio.Future()

asyncio.run(main())