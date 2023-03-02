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

    def show_hand_cards(self):
        hand_card_list = []
        for hand_card in self.hand_cards:
            hand_card_list.append(hand_card.show_card())
        return hand_card_list

    def show_real_cards(self):
        real_card_list = []
        for real_card in self.real_cards:
            real_card_list.append(real_card.show_card())
        return real_card_list


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
        self.game_id = str(uuid.uuid1())
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

    def get_queues_dict(self):
        if self.game_type == NORMAL_GAME:
            # 检查放的花火是否合格
            hanabiqueue_dict = {
                WHITE: self.writequeue,
                RED: self.redqueue,
                YELLOW: self.yellowqueue,
                BLUE: self.bluequeue,
                GREEN: self.greenqueue
            }
        else:
            hanabiqueue_dict = {
                WHITE: self.writequeue,
                RED: self.redqueue,
                YELLOW: self.yellowqueue,
                BLUE: self.bluequeue,
                GREEN: self.greenqueue,
                COLORFUL: self.colorfulqueue,
            }
        return hanabiqueue_dict

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

        self.curplayer = self.players[self.playerids[0]]

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
        correct = True
        if num_queue[len(card_queue)] == num:
            correct = True
        else:
            correct = False

        print("打出牌：", card.show_card())
        if correct == True: # 正确是加入列表
            card_queue.append(card)
        else:   # 错误时，剩余错误数减一，并把牌丢入弃牌堆
            print("出牌不合法")
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
        if self.tortime_leave == 0:
            self.end = True
            return


        finish_status = True

        queuelist = self.get_queues_dict()
        for hanabiqueue in queuelist:
            if hanabiqueue == [ONE, TWO, THREE, FOUR, FIVE]:
                pass
            else:
                finish_status = False
                break
        if finish_status == True:
            self.end = True
            return


        # 最终轮结束
        if id(self.lr_trigger) == id(self.curplayer):
            self.end = True
            return




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

        self.check_end()
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

        self.check_end()
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

        self.check_end()
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
        self.__draw_card(self.curplayer)

        self.check_end()
        self.end_turn_op()

    # ----------------------------------------------------

    # 信息展示相关 -----------------------------------------
    def get_score(self):
        hanabiqueue_dict = self.get_queues_dict()
        score = 0
        for key, value in hanabiqueue_dict.items():
            score += len(value)
        return score

    def get_openinfo(self):
        '''
        返回剩余提示次数，剩余失败次数，剩余卡数，弃牌堆，花火堆
        :return:
        '''
        tiptime_leave = self.tiptime_leave
        tortime_leave = self.tortime_leave
        undrawcards_num = len(self.undrawcards)

        dropcardgroup_list = []
        for dropcard in self.dropcardgroup:
            dropcardgroup_list.append(dropcard.show_card())

        hanabigroup = {
            WHITE: [card.show_card() for card in self.writequeue],
            RED: [card.show_card() for card in self.redqueue],
            YELLOW: [card.show_card() for card in self.yellowqueue],
            BLUE: [card.show_card() for card in self.bluequeue],
            GREEN: [card.show_card() for card in self.greenqueue]
        }
        if self.game_type == COLORFUL_GAME:
            hanabigroup[COLORFUL] = self.colorfulqueue

        return tiptime_leave, tortime_leave, undrawcards_num, dropcardgroup_list, hanabigroup


    def get_players_cards(self, playerid):
        '''
        按相对位置获取其他玩家真实卡牌，和该玩家在自己视角看到的自己牌
        :return:
        '''
        player = self.players[playerid]
        players_real_cards = []
        players_hand_cards = []
        for i in range(self.player_num - 1):
            player = player.next_player
            player_real_cards = player.show_real_cards()
            players_real_cards.append(player_real_cards)
            player_hand_cards = player.show_hand_cards()
            players_hand_cards.append(player_hand_cards)
        return players_real_cards, players_hand_cards

    def get_handcards(self, playerid):
        '''
        获取自己手卡
        :return:
        '''
        player = self.players[playerid]
        return player.show_hand_cards()

    def get_card_type_leave_num(self, playerid):
        '''
        获取自己视角下，剩余各种牌的张数（剩余牌堆+自己手牌得出）
        :param playerid:
        :return:
        '''
        player = self.players[playerids]
        cards_leave = player.real_cards+self.undrawcards
        cards_leave_dict = {
            WHITE: {ONE:0, TWO:0, THREE:0, FOUR:0, FIVE:0},
            RED: {ONE: 0, TWO: 0, THREE: 0, FOUR: 0, FIVE: 0},
            YELLOW: {ONE: 0, TWO: 0, THREE: 0, FOUR: 0, FIVE: 0},
            BLUE: {ONE: 0, TWO: 0, THREE: 0, FOUR: 0, FIVE: 0},
            GREEN: {ONE: 0, TWO: 0, THREE: 0, FOUR: 0, FIVE: 0},
        }
        if self.game_type == COLORFUL_GAME:
            cards_leave_dict[COLORFUL] = {ONE:0, TWO:0, THREE:0, FOUR:0, FIVE:0}
        for card in cards_leave:
            card_info = card.show_card()
            cards_leave_dict[card_info['color']][card_info['num']] += 1
        return cards_leave_dict


    def get_player_infomation(self, playerid):
        '''
        调用上面4个方法，即为玩家可获取的信息
        :param playerid:
        :return:
        '''
        score = self.get_score()
        tiptime_leave, tortime_leave, undrawcards_num, dropcardgroup_list, hanabigroup = self.get_openinfo()
        players_real_cards, players_hand_cards = self.get_players_cards(playerid)
        handcards = self.get_handcards(playerid)
        return {
            "open_info":{
                "score": score,
                "tiptime_leave": tiptime_leave,
                "tortime_leave": tortime_leave,
                "undrawcards_num": undrawcards_num,
                "dropcardgroup_list": dropcardgroup_list,
                "hanabigroup": hanabigroup
            },
            "personal_info":{
                "players_real_cards": players_real_cards,
                "players_hand_cards": players_hand_cards,
                "my_hand_cards": handcards,
                "cards_leave": self.get_card_type_leave_num(playerid)
            }
        }



if __name__ == '__main__':
    g0 = Game(3)    # 创建游戏房间
    g0.create_game()    # 开始游戏

    playerids = g0.playerids
    player0_info = g0.get_player_infomation(playerids[0])   # 玩家获取自己能看到的所有信息

    # 四种出牌方式
    g0.color_tips(playerids[0], 1, 1)
    # g0.num_tips(playerids[0], 1, 1)
    # g0.drop_card(playerids[0], 1)
    # g0.dis_card(playerids[0], 2)

    player0_info = g0.get_player_infomation(playerids[0])  # 玩家获取自己能看到的所有信息




