class Session():
    def __init__(self, session_id):
        self.session_id = session_id
    
    def set_name(self, name: str):
        self.name = name

    def set_lobby(self, lobby_id):
        self.lobby_id = lobby_id

    