'''
构造与房间进行连接的方式，与房间创建，游戏创建的方式
'''
import game
from define import *
import uuid
from error_types import GameError, RoomError


class Room:
    def __init__(self, name, holder_name, sid):
        self.name = name
        self.holderid = sid
        self.users = [(self.holderid, holder_name)]
        self.player_connect = {}
        self.game_start = False

    def enter_room(self, user_name, sid):
        # 未开始时可进入房间
        if self.game_start:
            raise GameError(GameError.GAME_START)
        userid = str(uuid.uuid1())
        self.users.append((userid, user_name))
        return uuid

    def create_game(self, game_type=NORMAL_GAME, tortime=3, tiptime=8):
        # 创建游戏，游戏开始
        if self.game_start:
            raise GameError(GameError.GAME_START)
        self.game = game.Game(len(self.users), game_type, tortime, tiptime)
        for playerid, user in zip(game.playerids, self.users):
            self.player_connect[playerid] = user
        self.game.create_game()

    def leave_room(self, sid):
        if self.game_start is False:
            for userid, user_name in self.users:
                if userid == sid:
                    self.users.remove((userid, user_name))
                    return
        else:
            for playerid, user_info in self.player_connect.items():
                if sid == user_info[0]:
                    self.player_connect[playerid] = (sid, user_info[1])
                    return

    def reconnect(self, sid, playerid):
        if playerid in self.player_connect.keys():
            user_info = self.player_connect[playerid]
            self.player_connect[playerid] = (sid, user_info[1])
            return
        raise RoomError(RoomError.PLAYERID_NOT_EXISTS)


    def disconnect(self, sid):
        for playerid, user_info in self.player_connect.items():
            if user_info[0] == sid:
                del playerid[playerid]

    def if_delete_room(self):
        if self.game_start is False:
            for userid, user_name in self.users:
                if userid == self.holderid:
                    return False
        else:
            for playerid, user_info in self.player_connect.items():
                if user_info[0] is not None:
                    return False
        return True

    def get_user_name(self, sid):
        if self.game_start is False:
            for userid, user_name in self.users:
                if userid == sid:
                    return user_name
        else:
            for playerid, user_info in self.player_connect.items():
                if sid == user_info[0]:
                    return user_info[1]

    def get_playerid(self, sid):
        for playerid, user_info in self.player_connect.items():
            if sid == user_info[0]:
                return playerid
