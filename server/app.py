from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import asyncio 
import sys 
import os
from setup.game_logic import Agent_logic
from pydantic import BaseModel 




app=FastAPI()

class request(BaseModel):
    num_food: int
    world_dimension: int
    num_episodes:int

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)



@app.get("/")
def read_root():
    return {"message": "Server is live."}

@app.post("/ailogic/")
async def Ailogic(req: request):
    try:
       result= Agent_logic(num_food=req.num_food, world_dimension= req.world_dimension, num_episodes=req.num_episodes)
       return result
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

# @app.websocket("/ws")
# async def websocket_endpoint(websocket:WebSocket):

#     global current_world_state

#     await websocket.accept()

#     print("Client connected via websockets")

#     try:
#         while True:
#             current_world_state=run_simulation_step(current_world_state)

#             await websocket.send_json(current_world_state)

#             await asyncio.sleep(0.1)

#     except WebSocketDisconnect:
#         print("Client disconnected")

#         current_world_state=init_game_state()
