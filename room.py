'''
构造与房间进行连接的方式，与房间创建，游戏创建的方式
'''
import game
from define import *
import uuid
from error_types import GameError


class Room:
    def __init__(self, name, holder_name, sid):
        self.name = name
        self.holderid = sid
        self.users = [(self.holderid, holder_name)]
        self.player_connect = {}
        self.game_start = False

    def enter_room(self, user_name, sid):
        if self.game_start:
            raise GameError(GameError.GAME_START)
        userid = str(uuid.uuid1())
        self.users.append((userid, user_name))
        return uuid

    def create_game(self, game_type=NORMAL_GAME, tortime=3, tiptime=8):
        if self.game_start:
            raise GameError(GameError.GAME_START)
        self.game = game.Game(len(self.users), game_type, tortime, tiptime)
        for playerid, user in zip(game.playerids, self.users):
            self.player_connect[playerid] = user[0]
        self.game.create_game()

    def leave_room(self, userid, user_name):
        self.users.remove((userid, user_name))

    def reconnect(self, sid, playerid):
        if playerid in self.player_connect.keys():
            self.player_connect[playerid] = sid


