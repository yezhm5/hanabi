import cards

hand_card_num_max = 5

class Player():
    def __init__(self):
        self.hand_cards = [cards.CardInHand() for i in range(5)]



class Game():
    '''
    游戏相关函数
    '''
    def __init__(self, player_num, game_type):
        pass



