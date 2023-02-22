class GameError(Exception):
    GAME_TYPE_ERROR = 400
    CARD_NUM_ERROR = 401
    CARD_COLOR_ERROR = 402


    NOT_CUR_PLAYER = 410
    PLAYER_NOT_EXISTS = 411
    CARD_POS_ERROR = 412
    TIPTIME_NOT_ENOUGH = 413


    GAME_END_ALRDY = 420

    dict_formatter = {
        GAME_TYPE_ERROR: "不存在该游戏模式".format,
        CARD_NUM_ERROR: "不存在该数字的卡片".format,
        CARD_COLOR_ERROR: "不存在该颜色的卡片".format,

        NOT_CUR_PLAYER: "未轮到你操作".format,
        PLAYER_NOT_EXISTS: "无法指示该玩家".format,
        CARD_POS_ERROR: "不存在该位置的卡牌".format,
        TIPTIME_NOT_ENOUGH: "提示次数不足，不可进行该操作".format,

        GAME_END_ALRDY: "游戏已结束，无法进行此操作".format,
    }

    def __init__(self, code: int, **kwargs): # real signature unknown
        self.code = code
        self.msg = self.dict_formatter[code](**kwargs)
