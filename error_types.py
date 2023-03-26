class GameError(Exception):
    GAME_TYPE_ERROR = 400
    CARD_NUM_ERROR = 401
    CARD_COLOR_ERROR = 402
    PLAYER_NUM_ERROR = 403
    GAME_START = 404


    NOT_CUR_PLAYER = 410
    PLAYER_NOT_EXISTS = 411
    CARD_POS_ERROR = 412
    TIPTIME_NOT_ENOUGH = 413
    DO_TYPE_NOT_EXISTS = 414


    GAME_END_ALRDY = 420

    dict_formatter = {
        GAME_TYPE_ERROR: "不存在该游戏模式".format,
        CARD_NUM_ERROR: "不存在该数字的卡片".format,
        CARD_COLOR_ERROR: "不存在该颜色的卡片".format,
        PLAYER_NUM_ERROR: "人数不正确，人数必须为2-5人".format(),
        GAME_START: "游戏已开始".format(),

        NOT_CUR_PLAYER: "未轮到你操作".format,
        PLAYER_NOT_EXISTS: "无法指示该玩家".format,
        CARD_POS_ERROR: "不存在该位置的卡牌".format,
        TIPTIME_NOT_ENOUGH: "提示次数不足，不可进行该操作".format,
        DO_TYPE_NOT_EXISTS: "不存在该操作类型".format,

        GAME_END_ALRDY: "游戏已结束，无法进行此操作".format,
    }

    def __init__(self, code: int, **kwargs): # real signature unknown
        self.code = code
        self.msg = self.dict_formatter[code](**kwargs)


class RoomError(Exception):
    ROOM_EXISTS = 300
    ROOM_NOT_EXISTS = 301
    NOT_HOLDER = 302
    PLAYERID_NOT_EXISTS = 303

    dict_formatter = {
        ROOM_EXISTS: "房间名已存在".format,
        ROOM_NOT_EXISTS: "房间名不存在".format,
        NOT_HOLDER: "你不是房主，不能进行该操作".format,
        PLAYERID_NOT_EXISTS: "你输入的玩家id不存在".format
    }

    def __init__(self, code: int, **kwargs): # real signature unknown
        self.code = code
        self.msg = self.dict_formatter[code](**kwargs)


