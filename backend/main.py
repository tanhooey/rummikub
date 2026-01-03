from typing import Union, Annotated
from fastapi import FastAPI, WebSocket, Response, Cookie, HTTPException, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from util import Lobby, Session
from util import get_random_string
from util import CreateGame, ResponseEnvelope, ConnectionManager
from typing import Dict
from fastapi.middleware.cors import CORSMiddleware

origins = [
    "http://localhost:5173",  # Removed trailing slash
]

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

cm = ConnectionManager()

lobbies: Dict[str, Lobby] = {}
sessions: Dict[str, Session] = {}


# @app.get("/")
# def get():
#     return HTMLResponse(html)

@app.get("/api/start_session")
def start_session(response: Response, session_id: Annotated[str | None, Cookie()] = None):
    # Generate a session
    if not session_id or session_id not in sessions:
        session_id = get_random_string(8)
        while session_id in sessions:
            session_id = get_random_string(16)
    response.set_cookie(
        key="session_id", 
        value=session_id,
        # SECURITY CRITICAL SETTINGS:
        httponly=True,  # Prevents JavaScript from reading this (stops XSS)
        secure=False,    # Only sends cookie over HTTPS
        samesite="none", # Protects against CSRF attacks
        max_age=3600    # Cookie expires in 1 hour (persistence)
    )

        # Add the session to the tracked sessions
    session = Session(session_id)
    sessions[session_id] = session
    return {"msg": "User sends nothing, but gets a cookie!"}
    
@app.post("/api/create_game")
def create_game(game: CreateGame, session_id: Annotated[str | None, Cookie()] = None) -> ResponseEnvelope[None]:
    # Update session object
    if not session_id or session_id not in sessions:
        raise HTTPException(status_code=403, detail="Session does not exist.")
    
    # Generate unique id for lobby
    host_name = game.player_name
    uuid = get_random_string()
    while uuid in lobbies:
        uuid = get_random_string()

    # Create player and add host
    new_lobby = Lobby(uuid)
    new_lobby.add_player(session_id)
    lobbies[uuid] = new_lobby

    current_session = sessions[session_id]
    current_session.set_lobby(uuid)
    current_session.set_name(host_name)
    response = f"Game {uuid} successfully created."
    
    return ResponseEnvelope(message=response)

@app.post("/api/join_game")
def join_game(game: CreateGame, session_id: Annotated[str | None, Cookie()] = None) -> ResponseEnvelope[None]:
    name = game.player_name
    game_id = game.game_id
    # Validate session
    if not session_id or session_id not in sessions:
        raise HTTPException(status_code=403, detail="Session does not exist.")

    # Check lobby exists
    if game_id not in lobbies:
        return ResponseEnvelope(status="false", message="Lobby doesn't exist.")

    # Add player to lobby and update session
    lobbies[game_id].add_player(session_id)
    current_session = sessions[session_id]
    current_session.set_lobby(game_id)
    current_session.set_name(name)

    return ResponseEnvelope(status="true", message="Successfully joined " + game_id + " as " + name + ".")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, session_id: Annotated[str | None, Cookie()] = None):
    if not session_id:
        raise HTTPException(status_code=403, detail="Session does not exist or not found.")
    await cm.connect(session_id, websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Find which lobby this session is in
            if session_id not in sessions:
                # Shouldn't happen because we validated above, but guard anyway
                raise HTTPException(status_code=403, detail="Session missing")

            current_session = sessions[session_id]
            game_id = getattr(current_session, 'lobby_id', None)
            if not game_id or game_id not in lobbies:
                # No lobby associated with this session
                await websocket.send_text("You are not in a game/lobby")
                continue

            current_game = lobbies[game_id]
            # Broadcast to all sessions in the lobby
            for session in current_game.players:
                await cm.send_to_session(session, data)
    except WebSocketDisconnect:
        cm.disconnect(session_id, websocket)

