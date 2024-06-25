import random
import pandas as pd

# 定義撲克牌
suits = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
deck = [rank + ' of ' + suit for suit in suits for rank in ranks]

def deal_poker_hands(deck, num_players=6):
    # 複製一副新的牌堆
    current_deck = deck[:]

    # 洗牌
    random.shuffle(current_deck)

    hands = {f'Player {i+1}': [] for i in range(num_players)}
    community_cards = []

    # 發給每個玩家兩張牌
    for i in range(num_players):
        hands[f'Player {i+1}'].append(current_deck.pop())
        hands[f'Player {i+1}'].append(current_deck.pop())

    # 發社區牌：三張翻牌
    community_cards.append(current_deck.pop())
    community_cards.append(current_deck.pop())
    community_cards.append(current_deck.pop())

    # 發第四張轉牌
    community_cards.append(current_deck.pop())

    # 發第五張河牌
    community_cards.append(current_deck.pop())

    return hands, community_cards

# 記錄100萬局
num_games = 100000
results = []

positions = ['Button', 'Small Blind', 'Big Blind', 'UTG', 'HighJack', 'CutOff']

for game_number in range(num_games):
    hands, community_cards = deal_poker_hands(deck)

    game_result = {'Game Number': game_number + 1}

    for i, position in enumerate(positions):
        game_result[f'{position} Hand 1'] = hands[f'Player {i+1}'][0]
        game_result[f'{position} Hand 2'] = hands[f'Player {i+1}'][1]

    for j in range(5):
        game_result[f'Community Card {j+1}'] = community_cards[j]

    results.append(game_result)

# 將結果轉為DataFrame
df = pd.DataFrame(results)

# 顯示前幾局結果
print(df.head())

# 將結果保存到CSV文件
df.to_csv('Texas_Holdem/poker_games_detailed2.csv', index=False)
