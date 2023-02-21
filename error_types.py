class GameError(Exception):
    GAME_TYPE_ERROR = 400
    CARD_NUM_ERROR = 401
    CARD_COLOR_ERROR = 402


    NOT_CUR_PLAYER = 410
    PLAYER_NOT_EXISTS = 411

    dict_formatter = {
        GAME_TYPE_ERROR: "不存在该游戏模式".format,
        CARD_NUM_ERROR: "不存在该数字的卡片".format,
        CARD_COLOR_ERROR: "不存在该颜色的卡片".format,

        NOT_CUR_PLAYER: "未轮到你操作".format,
        PLAYER_NOT_EXISTS: "无法指示该玩家".format,
    }

    def __init__(self, code: int, **kwargs): # real signature unknown
        self.code = code
        self.msg = self.dict_formatter[code](**kwargs)
