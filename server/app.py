from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import asyncio 
import sys 
import os
from setup.game_logic import init_game_state, run_simulation_step



app=FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

current_world_state=init_game_state()


@app.get("/")
def read_root():
    return {"message": "Server is live."}

@app.websocket("/ws")
async def websocket_endpoint(websocket:WebSocket):

    global current_world_state

    await websocket.accept()

    print("Client connected via websockets")

    try:
        while True:
            current_world_state=run_simulation_step(current_world_state)

            await websocket.send_json(current_world_state)

            await asyncio.sleep(0.1)

    except WebSocketDisconnect:
        print("Client disconnected")

        current_world_state=init_game_state()
