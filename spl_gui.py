import http.server
import socketserver
import threading
import usb.core
import usb.util
import asyncio
import websockets
import json
import os
from wensn import connect, readSPL

PORT = 8000

# SPL mérő csatlakoztatása
dev = connect()
print("SPL mérő csatlakoztatva.")

# HTTP szerver külön szálon
def start_http_server():
    os.chdir("frontend")
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", PORT), handler) as httpd:
        print(f"HTTP szerver fut a http://localhost:{PORT} címen")
        httpd.serve_forever()

threading.Thread(target=start_http_server, daemon=True).start()

# Új típusú WebSocket handler Python 3.13-hoz
async def spl_server(connection):
    print("WebSocket kliens csatlakozott")
    try:
        while True:
            dB, range_mode, weight, speed = readSPL(dev)
            spl_data = {
                "spl": round(dB, 1),
                "range": range_mode,
                "weight": weight,
                "speed": speed
            }
            await connection.send(json.dumps(spl_data))
            await asyncio.sleep(1)
    except websockets.exceptions.ConnectionClosed:
        print("WebSocket kliens bontotta a kapcsolatot")

# Async main
async def main():
    print("WebSocket szerver indul a ws://localhost:8001 címen")
    async with websockets.serve(spl_server, "localhost", 8001):
        await asyncio.Future()

# Indítás
asyncio.run(main())
