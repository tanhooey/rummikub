from typing import Set, List
class Lobby:
    def __init__(self, id: str):
        self.id = id
        self.players: Set[str] = set([])

    def add_player(self, player_id: str):
        self.players.add(player_id)
    
