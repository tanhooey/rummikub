from typing import Union, Annotated
from fastapi import FastAPI, WebSocket, Response, Cookie, HTTPException, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from util import Lobby, Session
from util import get_random_string
from util import CreateGame, ResponseEnvelope, ConnectionManager
from typing import Dict

app = FastAPI()
cm = ConnectionManager()

lobbies: Dict[str, Lobby] = {}
sessions: Dict[str, Session] = {}

html = """
<!DOCTYPE html>
<html>
    <head>
        <meta charset="utf-8" />
        <title>Rummikub — Lobby</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 2rem auto; }
            label { display: inline-block; width: 110px; }
            #messages { margin-top: 1rem; list-style: none; padding: 0; }
            #messages li { padding: 6px 8px; border-bottom: 1px solid #eee; }
            #current_game { margin-top: 0.5rem; font-weight: bold; }
        </style>
    </head>
    <body>
        <h1>Rummikub — Lobby UI</h1>

        <div id="session_info">Starting session...</div>

        <div id="lobby_ui" style="display:none; margin-top:1rem;">
            <div>
                <label for="player_name">Your name</label>
                <input id="player_name" placeholder="Enter your name" />
            </div>
            <div style="margin-top:8px;">
                <button id="create_btn">Create Game</button>
            </div>
            <div style="margin-top:10px;">
                <label for="join_game_id">Join Game ID</label>
                <input id="join_game_id" placeholder="Game id" />
                <button id="join_btn">Join Game</button>
            </div>
            <div id="current_game"></div>
            <div id="lobby_messages"></div>
        </div>

        <form id="chat_form" onsubmit="sendMessage(event)" style="margin-top:1rem; display:none;">
            <input type="text" id="messageText" autocomplete="off" placeholder="Type message or game action" />
            <button>Send</button>
        </form>

        <ul id="messages"></ul>

        <script>
            let ws = null;
            let currentGame = null;

            function appendMsg(text) {
                const messages = document.getElementById('messages');
                const li = document.createElement('li');
                li.textContent = text;
                messages.appendChild(li);
                window.scrollTo(0, document.body.scrollHeight);
            }

            function startSession() {
                // Request a session cookie from backend; include credentials so cookie is set
                fetch('/api/start_session', { credentials: 'include' })
                    .then(res => res.json())
                    .then(data => {
                        document.getElementById('session_info').innerText = data.msg;
                        document.getElementById('lobby_ui').style.display = 'block';
                        connectWS();
                    })
                    .catch(err => {
                        document.getElementById('session_info').innerText = 'Failed to start session.';
                        console.error(err);
                    });
            }

            function connectWS() {
                const protocol = location.protocol === 'https:' ? 'wss://' : 'ws://';
                ws = new WebSocket(protocol + window.location.host + '/ws');

                ws.onopen = () => {
                    appendMsg('Connected to websocket');
                    document.getElementById('chat_form').style.display = 'block';
                };

                ws.onmessage = function(event) {
                    appendMsg(event.data);
                };

                ws.onclose = function() {
                    appendMsg('WebSocket closed');
                    document.getElementById('chat_form').style.display = 'none';
                };

                ws.onerror = function(e) { console.error('WS error', e); };
            }

            function createGame() {
                const name = document.getElementById('player_name').value || 'Host';
                fetch('/api/create_game', {
                    method: 'POST',
                    credentials: 'include',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ player_name: name })
                })
                .then(r => r.json())
                .then(data => {
                    // ResponseEnvelope returns message property
                    const msg = data.message || data.msg || JSON.stringify(data);
                    document.getElementById('current_game').innerText = msg;
                    // Try to extract uuid from message if present
                    const m = msg.match(/Game\s+(\w+)\s+successfully/);
                    if (m) currentGame = m[1];
                })
                .catch(err => {
                    console.error(err);
                    appendMsg('Failed to create game');
                });
            }

            function joinGame() {
                const name = document.getElementById('player_name').value || 'Player';
                const id = document.getElementById('join_game_id').value;
                if (!id) { appendMsg('Enter a game id to join'); return; }
                fetch('/api/join_game', {
                    method: 'POST',
                    credentials: 'include',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ player_name: name, game_id: id })
                })
                .then(r => r.json())
                .then(data => {
                    const msg = data.message || JSON.stringify(data);
                    document.getElementById('current_game').innerText = msg;
                    if (data.status === 'true') currentGame = id;
                })
                .catch(err => {
                    console.error(err);
                    appendMsg('Failed to join game');
                });
            }

            function sendMessage(event) {
                event.preventDefault();
                const input = document.getElementById('messageText');
                const text = input.value;
                if (!text) return;
                if (!ws || ws.readyState !== WebSocket.OPEN) {
                    appendMsg('WebSocket is not connected');
                    return;
                }
                ws.send(text);
                input.value = '';
            }

            document.addEventListener('DOMContentLoaded', function() {
                document.getElementById('create_btn').addEventListener('click', createGame);
                document.getElementById('join_btn').addEventListener('click', joinGame);
                startSession();
            });
        </script>
    </body>
</html>
"""

@app.get("/")
def get():
    return HTMLResponse(html)

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
        samesite="lax", # Protects against CSRF attacks
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

