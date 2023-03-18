'''
构造与房间进行连接的方式，与房间创建，游戏创建的方式
'''
import game
from define import *
import uuid

class Room:
    def __init__(self, name, holder_name):
        self.name = name
        self.holderid = str(uuid.uuid1())
        self.players = [(self.holderid, holder_name)]

    def enter_room(self, player_name):
        playerid = str(uuid.uuid1())
        self.players.append((playerid, player_name))
        return uuid

    def create_game(self, game_type=NORMAL_GAME, tortime=3, tiptime=8):
        self.game = game.Game(len(self.players), game_type, tortime, tiptime)

    def leave_room(self, playerid, player_name):
        self.players.remove((playerid, player_name))




