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
from define import *



class CardInHand():
    '''
    表示玩家自己手上的反面表示的卡
    '''


    def __init__(self, game_type=NORMAL_GAME):
        self.game_type = game_type
        self.unknow = True
        self.color_known = False
        self.num_known = False
        if game_type == NORMAL_GAME:
            self.colors = {
                RED, YELLOW, BLUE, GREEN, WHITE
            }
        elif game_type == COLORFUL_GAME:
            self.colors = {
                RED, YELLOW, BLUE, GREEN, WHITE, COLORFUL
            }
        else:
            ge = GameError(code=GameError.GAME_TYPE_ERROR)
            raise ge
        self.nums = {
            ONE, TWO, THREE, FOUR, FIVE
        }

    def check_color(self, color):
        if self.game_type == NORMAL_GAME:
            colors_include = {RED, YELLOW, BLUE, GREEN, WHITE}
        elif self.game_type == COLORFUL_GAME:
            colors_include = {RED, YELLOW, BLUE, GREEN, WHITE, COLORFUL}
        else:
            ge = GameError(code=GameError.GAME_TYPE_ERROR)
            raise ge

        if color not in colors_include:
            ge = GameError(code=GameError.CARD_COLOR_ERROR)
            raise ge

    def check_num(self, num):
        if num not in {ONE, TWO, THREE, FOUR, FIVE}:
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
    


class Card():
    def __init__(self, color, num):
        self.color = color
        self.num = num




