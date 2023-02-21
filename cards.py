'''
所有牌的信息
颜色：red, yellow, blue , green, white, colorful
数字：1,2,3,4,5
普通颜色各数字对应张数：
    1 ： 3张
    2 ： 2张
    3 ： 2张
    4 ： 2张
    5 ： 1张
彩色各数字对应张数：
    1 ： 1张
    2 ： 1张
    3 ： 1张
    4 ： 1张
    5 ： 1张
'''
from error_types import GameError

class card():
    RED = 1
    YELLOW = 2
    BLUE = 3
    GREEN = 4
    WHITE = 5
    COLORFUL = 6

    ONE = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5

    def __init__(self, game_type='normal'):
        self.game_type = game_type
        self.unknow = True
        self.color_known = False
        self.num_known = False
        if game_type == 'normal':
            self.colors = {
                self.RED, self.YELLOW, self.BLUE, self.GREEN, self.WHITE
            }
        elif game_type == "colorful":
            self.colors = {
                self.RED, self.YELLOW, self.BLUE, self.GREEN, self.WHITE, self.COLORFUL
            }
        else:
            ge = GameError(code=GameError.GAME_TYPE_ERROR)
            raise ge
        self.nums = {
            self.ONE, self.TWO, self.THREE, self.FOUR, self.FIVE
        }

    def check_color(self, color):
        if self.game_type == 'normal':
            colors_include = {self.RED, self.YELLOW, self.BLUE, self.GREEN, self.WHITE}
        elif self.game_type == "colorful":
            colors_include = {self.RED, self.YELLOW, self.BLUE, self.GREEN, self.WHITE, self.COLORFUL}
        else:
            ge = GameError(code=GameError.GAME_TYPE_ERROR)
            raise ge

        if color not in colors_include:
            ge = GameError(code=GameError.CARD_COLOR_ERROR)
            raise ge

    def check_num(self, num):
        if num not in {self.ONE, self.TWO, self.THREE, self.FOUR, self.FIVE}:
            ge = GameError(code=GameError.CARD_NUM_ERROR)
            raise ge

    def set_color(self, color):
        self.check_color(color)
        self.unknow = False
        self.color_known = True
        self.colors = {color}

    def set_num(self, num):
        self.check_num(num)
        self.unknow = False
        self.num_known = True
        self.nums = {num}

    def remove_color(self, color):
        self.check_color(color)
        self.unknow = False
        self.colors.remove(color)
        if len(self.colors) == 1:
            self.color_known = True

    def remove_num(self, num):
        self.check_num(num)
        self.unknow = False
        self.nums.remove(num)
        if len(self.nums) == 1:
            self.num_known = True
    



