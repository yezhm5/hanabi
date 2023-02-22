from cards import CardInHand, Card
import uuid
from define import *
from error_types import GameError
import random

hand_card_num_max = 5

class Player():
    def __init__(self, next_player=None):
        self.hand_cards = []
        self.real_cards = []
        self.next_player = next_player

    def set_next_player(self, next_player):
        self.next_player = next_player

    def draw_card(self, card, game_type):
        self.real_cards.append(card)
        self.hand_cards.append(CardInHand(game_type=game_type))

    def dis_card(self, card_relpos):
        if card_relpos >= len(self.hand_cards) or card_relpos < 0:
            raise GameError(code=GameError.CARD_POS_ERROR)
        self.hand_cards.pop(card_relpos)
        return self.real_cards.pop(card_relpos)

    def color_tips(self, color):
        for hand_card, real_card in zip(self.hand_cards, self.real_cards):
            if real_card.color==color:
                hand_card.set_color(color)
            else:
                hand_card.remove_color(color)

    def num_tips(self, num):
        for hand_card, real_card in zip(self.hand_cards, self.real_cards):
            if real_card.num == num:
                hand_card.set_num(num)
            else:
                hand_card.remove_num(num)

class Game():
    '''
    游戏相关函数
    '''
    def __init__(self, player_num, game_type=NORMAL_GAME, tortime=3, tiptime=8):
        '''

        :param player_num: 2 - 5
        :param game_type:
        :param tortime: 错误容忍次数
        :param tiptime: 起始提示次数
        '''
        # 设定随机uuid，作为请求时的用户id标识
        self.player_num = player_num
        self.playerids = [str(uuid.uuid1()) for i in range(player_num)]
        self.players = {playerid:Player() for playerid in self.playerids}
        for i in range(player_num):
            playerid = self.playerids[i]
            playerid_next = self.playerids[(i+1)%player_num]
            self.players[playerid].set_next_player(self.players[playerid_next])
        # 当前操作玩家
        self.curplayer = self.players[self.playerids[0]]

        self.check_game_type(game_type)
        self.game_type = game_type
        self.tortime = tortime
        self.tiptime = tiptime
        self.tortime_leave = tortime
        self.tiptime_leave = tiptime

        self.lastround = False  # 是否进入最后一轮
        self.lr_trigger = None  # 触发最后一轮的玩家
        self.end = False

        self.undrawcards = []   # 未抽牌堆
        self.dropcardgroup = [] # 弃牌堆

        # 花火队列
        self.writequeue = []    # 白色花火队列
        self.redqueue = []    # 白色花火队列
        self.yellowqueue = []    # 红色花火队列
        self.bluequeue = []    # 黄色花火队列
        self.greenqueue = []    # 蓝色花火队列
        self.colorfulqueue = []    # 绿色花火队列



    def check_game_type(self, game_type):
        if game_type not in [NORMAL_GAME, COLORFUL_GAME]:
            raise GameError(code=GameError.GAME_TYPE_ERROR)

    def cards_init(self):
        undrawcards = []

        card_type_num = {
            ONE : 3,
            TWO : 2,
            THREE : 2,
            FOUR : 2,
            FIVE : 1
        }
        for color in [WHITE, RED, YELLOW, BLUE, GREEN]:
            for num in [ONE, TWO, THREE, FOUR, FIVE]:
                for i in range(card_type_num[num]):
                    card = Card(color, num)
                    undrawcards.append(card)

        if self.game_type==COLORFUL_GAME:
            for num in [ONE, TWO, THREE, FOUR, FIVE]:
                card = Card(COLORFUL, num)
                undrawcards.append(card)

        random.shuffle(undrawcards)
        self.undrawcards = undrawcards

    def __draw_card(self, player):
        if len(self.undrawcards) > 0:
            player.draw_card(self.undrawcards.pop(0), self.game_type)

    def create_game(self):
        # 初始化卡组
        self.cards_init()

        # 每人抽取5张卡
        for i in range(STARTHANDCARDNUM):
            for playerid in self.playerids:
                player = self.players[playerid]
                self.__draw_card(player)

    def tiptime_add(self):
        if self.tiptime_leave < self.tiptime:
            self.tiptime_leave += 1

    def next_player(self):
        self.curplayer = self.curplayer.next_player

    def end_unable(fn):
        def wrapTheFunction(self, *args, **kwargs):
            if self.end == True:
                raise GameError(code=GameError.GAME_END_ALRDY)
            fn(self, *args, **kwargs)
        return wrapTheFunction


    def end_turn_op(self):
        '''
        1. 检测是否进入最后一轮
        2. 检测是否结束游戏
        3. 轮到下家操作
        :return:
        '''
        self.check_end_round()
        self.check_end()
        self.next_player()


    def check_end_round(self):
        if self.lastround == False and len(self.undrawcards) == 0:
            self.lastround = True
            self.lr_trigger = self.curplayer

    def check_hanabi(self, card):
        # 检查放的花火是否合格
        hanabiqueue_dict = {
            WHITE: self.writequeue,
            RED: self.redqueue,
            YELLOW: self.yellowqueue,
            BLUE: self.bluequeue,
            GREEN: self.greenqueue,
            COLORFUL: self.colorfulqueue,
        }
        num_queue = [ONE, TWO, THREE, FOUR, FIVE]

        color = card.color
        num = card.num

        card_queue = hanabiqueue_dict[color]
        card_queue.append(card)
        num_queue_tmp = [card.num for card in card_queue]

        correct = True
        for num_real, num_right in zip(num_queue_tmp, num_queue):
            if num_real != num_right:
                correct = False
                break
        if correct == True:
            pass
        else:
            card = card_queue.pop()
            self.tortime_leave -= 1
            self.dropcardgroup.append(card)




    def check_curplayer(self, playerid):
        if id(self.players[playerid]) != id(self.curplayer):
            raise GameError(code=GameError.NOT_CUR_PLAYER)

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

    def check_relpos(self, relpos):
        if relpos < 1 or relpos > self.player_num - 1:
            raise GameError(code=GameError.PLAYER_NOT_EXISTS)

    def check_tiptime(self):
        if self.tiptime_leave <= 0:
            raise GameError(code=GameError.TIPTIME_NOT_ENOUGH)


    def check_end(self):
        '''
        检测是否游戏结束
        1.失败次数全部用完
        2.所有组合完成
        3.最后一张牌抽走后，所有人在轮流进行最后一回合
        :return:
        '''
        pass


    # 四种操作：颜色提示，数字提示，弃牌，打牌 ------------------------------------
    @end_unable
    def color_tips(self, playerid, relpos, color):
        '''
        指示一位玩家一种颜色
        :param playerid: 玩家id
        :param relpos: 被指示的玩家的相对位置
        :param color: 指示的颜色
        :return:
        '''

        self.check_curplayer(playerid)
        self.check_relpos(relpos)
        self.check_color(color)
        self.check_tiptime()

        rel_player = self.curplayer
        for i in range(relpos):
            rel_player = rel_player.next_player
        rel_player.color_tips(color)
        self.tiptime_leave -= 1


        # 回合结束操作
        self.end_turn_op()

    @end_unable
    def num_tips(self, playerid, relpos, num):
        '''
        指示一位玩家一种数字
        :param playerid:
        :param relpos:
        :param color:
        :return:
        '''
        self.check_curplayer(playerid)
        self.check_relpos(relpos)
        self.check_num(num)
        self.check_tiptime()

        rel_player = self.curplayer
        for i in range(relpos):
            rel_player = rel_player.next_player
        rel_player.num_tips(num)
        self.tiptime_leave -= 1

        # 回合结束操作
        self.end_turn_op()


    @end_unable
    def drop_card(self, playerid, card_relpos):
        '''
        弃掉一张牌，拿到一个提示点，提示点上限不能超
        :param playerid:
        :param card_relpos:
        :return:
        '''
        self.check_curplayer(playerid)
        # 丢弃卡牌到弃牌堆
        card = self.curplayer.dis_card(card_relpos)
        self.dropcardgroup.append(card)

        # 抽卡
        self.__draw_card(self.curplayer)
        # 提示次数增加
        self.tiptime_add()

        # 回合结束操作
        self.end_turn_op()

    @end_unable
    def dis_card(self, playerid, card_relpos):
        '''
        打出一张牌，检查牌是否符合打出条件，若符合，则打出
        :param playerid:
        :param card_relpos:
        :return:
        '''
        self.check_curplayer(playerid)
        # 打出牌
        card = self.curplayer.dis_card(card_relpos)
        self.check_hanabi(card)

        self.end_turn_op()

    # ----------------------------------------------------

    # 信息展示相关 -----------------------------------------
    def get_scores(self):
        pass

    def get_openinfo(self):
        pass

    def get_players_cards(self):
        pass

    def get_handcards(self):
        pass

    def get_player_infomation(self, playerid):
        pass



if __name__ == '__main__':
    game = Game(3, NORMAL_GAME)
    # game.end = True
    player_id = game.playerids[0]
    game.drop_card(player_id, 0)